import os
import io
import json
import asyncio
import concurrent.futures
from urllib.parse import urljoin
from datetime import datetime, timedelta
from html import escape

import httpx
import uvicorn
import uvloop
from gunicorn.app.base import BaseApplication
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, FileResponse, JSONResponse, RedirectResponse, StreamingResponse
from starlette.background import BackgroundTask
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from searx import brand
from searx.exceptions import SearxParameterException
from searx.query import RawTextQuery
from searx.settings import (
    settings, searx_debug,
    default_theme, templates_path, themes, result_templates,
    static_path, static_files,
    global_favicons
)
from searx.engines import (
    categories, engines, engine_shortcuts, get_engines_stats, initialize_engines
)
from searx.plugins import plugins
from searx.plugins.oa_doi_rewrite import get_doi_resolver
from searx.utils import html_to_text, gen_useragent, dict_subset, match_language
from searx.preferences import Preferences, LANGUAGE_CODES
from searx.answerers import answerers
from searx.autocomplete import searx_bang, backends as autocomplete_backends
from searx.search import SearchWithPlugins
from searx.web.proxy import proxify, image_proxify, check_hmac_for_url, add_protocol
from searx.webadapter import get_search_query_from_webapp, get_selected_categories
from searx.webutils import UnicodeWriter, highlight_content, prettify_url, is_flask_run_cmdline
from searx.webapp import (
    _get_ordered_categories, rtl_locales, VERSION_STRING, logger
)
from searx.web.middleware import pre_request
from searx.web.templates import render, get_current_theme_name


client = None
routes = [
    Mount('/static', StaticFiles(directory=static_path), name='static'),
]
executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)


# FIXME : Babel
def format_date(o):
    return str(o)


def get_base_url(request):
    return request.url_for('index')


async def startup():
    global client
    client = httpx.AsyncClient(http2=True, timeout=settings['outgoing']['request_timeout'])
    print('Ready to go')


async def shutdown():
    global client
    await client.aclose()
    print('shutdown done')


app = Starlette(routes=routes, on_startup=[startup], on_shutdown=[shutdown], debug=True)


@app.exception_handler(404)
async def not_found(request, exc):
    await pre_request(request)
    return render(request, '404.html', status_code=404)


@app.route('/', methods=['GET', 'POST'])
async def index(request):
    """Render index page."""
    await pre_request(request)

    # redirect to search if there's a query in the request
    if request.state.form.get('q'):
        return RedirectResponse(request.url_for('search'), status_code=308)

    return render(request,
                  'index.html',
                  selected_categories=get_selected_categories(request.state.preferences, None),)


def search_error(request, output_format, error_message, status_code=400):
    if output_format == 'json':
        return JSONResponse({'error': error_message}, status_code=status_code)
    elif output_format == 'csv':
        response = PlainTextResponse('', media_type='application/csv', status_code=status_code)
        cont_disp = 'attachment;Filename=searx.csv'
        response.headers.add('Content-Disposition', cont_disp)
        return response
    elif output_format == 'rss':
        return render(
            request,
            'opensearch_response_rss.xml',
            media_type='text/xml',
            results=[],
            q=request.state.form['q'] if 'q' in request.state.form else '',
            number_of_results=0,
            base_url=get_base_url(request),
            error_message=error_message,
            override_theme='__common__',
            status_code=status_code,
        )
    else:
        # html
        request.state.errors.append(request.state.gettext('search error'))
        return render(
            request,
            'index.html',
            selected_categories=get_selected_categories(request.state.preferences, request.state.form),
            status_code=status_code,
        )


@app.route('/search', methods=["GET", "POST"])
async def search(request):
    await pre_request(request)
    """Search query in q and return results.

    Supported outputs: html, json, csv, rss.
    """

    # output_format
    output_format = request.state.form.get('format', 'html')
    if output_format not in ['html', 'csv', 'json', 'rss']:
        output_format = 'html'

    # check if there is query
    if not request.state.form.get('q'):
        if output_format == 'html':
            return render(
                request,
                'index.html',
                selected_categories=get_selected_categories(request.preferences, request.state.form),
            )
        else:
            return search_error(request, output_format, 'No query', status_code=400)

    # search
    search_query = None
    raw_text_query = None
    result_container = None
    try:
        loop = asyncio.get_event_loop()
        search_query, raw_text_query, _, _ = get_search_query_from_webapp(request.state.preferences, request.state.form)
        # search = Search(search_query) #  without plugins
        search = SearchWithPlugins(search_query, request.state.user_plugins, request)
        # FIXME: SearchWithPlugins should be async
        result_container = await loop.run_in_executor(executor, search.search)
    except Exception as e:
        # log exception
        logger.exception('search error')

        # is it an invalid input parameter or something else ?
        if (issubclass(e.__class__, SearxParameterException)):
            return search_error(request, output_format, e.message, status_code=400)
        else:
            return search_error(request, output_format, request.state.gettext('search error'), status_code=500)

    # results
    results = result_container.get_ordered_results()
    number_of_results = result_container.results_number()
    if number_of_results < result_container.results_length():
        number_of_results = 0

    # checkin for a external bang
    if result_container.redirect_url:
        return RedirectResponse(result_container.redirect_url)

    # UI
    advanced_search = request.state.form.get('advanced_search', None)

    # Server-Timing header
    request.state.timings = result_container.get_timings()

    # output
    for result in results:
        if output_format == 'html':
            if 'content' in result and result['content']:
                result['content'] = highlight_content(escape(result['content'][:1024]), search_query.query)
            if 'title' in result and result['title']:
                result['title'] = highlight_content(escape(result['title'] or ''), search_query.query)
        else:
            if result.get('content'):
                result['content'] = html_to_text(result['content']).strip()
            # removing html content and whitespace duplications
            result['title'] = ' '.join(html_to_text(result['title']).strip().split())

        if 'url' in result:
            result['pretty_url'] = prettify_url(result['url'])

        # TODO, check if timezone is calculated right
        if 'publishedDate' in result:
            try:  # test if publishedDate >= 1900 (datetime module bug)
                result['pubdate'] = result['publishedDate'].strftime('%Y-%m-%d %H:%M:%S%z')
            except ValueError:
                result['publishedDate'] = None
            else:
                if result['publishedDate'].replace(tzinfo=None) >= datetime.now() - timedelta(days=1):
                    timedifference = datetime.now() - result['publishedDate'].replace(tzinfo=None)
                    minutes = int((timedifference.seconds / 60) % 60)
                    hours = int(timedifference.seconds / 60 / 60)
                    if hours == 0:
                        result['publishedDate'] = request.state.gettext('{minutes} minute(s) ago').\
                            format(minutes=minutes)
                    else:
                        result['publishedDate'] = request.state.gettext('{hours} hour(s), {minutes} minute(s) ago').\
                            format(hours=hours, minutes=minutes)  # noqa
                else:
                    result['publishedDate'] = format_date(result['publishedDate'])

    if output_format == 'json':
        return PlainTextResponse(json.dumps({'query': search_query.query,
                                             'number_of_results': number_of_results,
                                             'results': results,
                                             'answers': list(result_container.answers),
                                             'corrections': list(result_container.corrections),
                                             'infoboxes': result_container.infoboxes,
                                             'suggestions': list(result_container.suggestions),
                                             'unresponsive_engines': __get_translated_errors(request, result_container.unresponsive_engines)},  # noqa
                                            default=lambda item: list(item) if isinstance(item, set) else item,
                                            ensure_ascii=False,
                                            allow_nan=False,
                                            indent=None,
                                            separators=(",", ":")),
                                 media_type='application/json')
    elif output_format == 'csv':
        csv = UnicodeWriter(io.StringIO())
        keys = ('title', 'url', 'content', 'host', 'engine', 'score', 'type')
        csv.writerow(keys)
        for row in results:
            row['host'] = row['parsed_url'].netloc
            row['type'] = 'result'
            csv.writerow([row.get(key, '') for key in keys])
        for a in result_container.answers:
            row = {'title': a, 'type': 'answer'}
            csv.writerow([row.get(key, '') for key in keys])
        for a in result_container.suggestions:
            row = {'title': a, 'type': 'suggestion'}
            csv.writerow([row.get(key, '') for key in keys])
        for a in result_container.corrections:
            row = {'title': a, 'type': 'correction'}
            csv.writerow([row.get(key, '') for key in keys])
        csv.stream.seek(0)
        response = PlainTextResponse(csv.stream.read(), media_type='application/csv')
        cont_disp = 'attachment;Filename=searx_-_{0}.csv'.format(search_query.query)
        response.headers.add('Content-Disposition', cont_disp)
        return response

    elif output_format == 'rss':
        return render(
            request,
            'opensearch_response_rss.xml',
            media_type='text/xml',
            results=results,
            answers=result_container.answers,
            corrections=result_container.corrections,
            suggestions=result_container.suggestions,
            q=request.form['q'],
            number_of_results=number_of_results,
            base_url=get_base_url(request),
            override_theme='__common__',
        )

    # HTML output format

    # suggestions: use RawTextQuery to get the suggestion URLs with the same bang
    suggestion_urls = list(map(lambda suggestion: {
                               'url': raw_text_query.changeQuery(suggestion).getFullQuery(),
                               'title': suggestion
                               },
                               result_container.suggestions))

    correction_urls = list(map(lambda correction: {
                               'url': raw_text_query.changeQuery(correction).getFullQuery(),
                               'title': correction
                               },
                               result_container.corrections))
    #
    return render(
        request,
        'results.html',
        results=results,
        q=request.state.form['q'],
        selected_categories=search_query.categories,
        pageno=search_query.pageno,
        time_range=search_query.time_range,
        number_of_results=format_date(number_of_results),
        advanced_search=advanced_search,
        suggestions=suggestion_urls,
        answers=result_container.answers,
        corrections=correction_urls,
        infoboxes=result_container.infoboxes,
        paging=result_container.paging,
        unresponsive_engines=__get_translated_errors(request, result_container.unresponsive_engines),
        current_language=match_language(search_query.lang,
                                        LANGUAGE_CODES,
                                        fallback=request.state.preferences.get_value("language")),
        base_url=get_base_url(request),
        theme=get_current_theme_name(request),
        favicons=global_favicons[themes.index(get_current_theme_name(request))],
        timeout_limit=request.state.form.get('timeout_limit', None)
    )


def __get_translated_errors(request, unresponsive_engines):
    translated_errors = []
    for unresponsive_engine in unresponsive_engines:
        error_msg = request.state.gettext(unresponsive_engine[1])
        if unresponsive_engine[2]:
            error_msg = "{} {}".format(error_msg, unresponsive_engine[2])
        translated_errors.append((unresponsive_engine[0], error_msg))
    return translated_errors


@app.route('/autocompleter', methods=['GET', 'POST'])
async def autocompleter(request):
    await pre_request(request)
    """Return autocompleter results"""

    # set blocked engines
    disabled_engines = request.state.preferences.engines.get_disabled()

    # parse query
    raw_text_query = RawTextQuery(request.state.form.get('q', ''), disabled_engines)

    # check if search query is set
    if not raw_text_query.getQuery():
        return '', 400

    # run autocompleter
    loop = asyncio.get_event_loop()
    autocomplete = request.state.preferences.get_value('autocomplete')
    completer = autocomplete_backends.get(autocomplete)

    # parse searx specific autocompleter results like !bang
    raw_results = searx_bang(raw_text_query)

    # normal autocompletion results only appear if no inner results returned
    # and there is a query part besides the engine and language bangs
    if len(raw_results) == 0 and completer and (len(raw_text_query.query_parts) > 1 or
                                                (len(raw_text_query.languages) == 0 and
                                                 not raw_text_query.specific)):
        # get language from cookie
        language = request.state.preferences.get_value('language')
        if not language or language == 'all':
            language = 'en'
        else:
            language = language.split('-')[0]
        # run autocompletion
        result = await loop.run_in_executor(executor, completer, raw_text_query.getQuery(), language)
        raw_results.extend(result)

    # parse results (write :language and !engine back to result string)
    results = []
    for result in raw_results:
        raw_text_query.changeQuery(result)

        # add parsed result
        results.append(raw_text_query.getFullQuery())

    # return autocompleter results
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JSONResponse(results,
                            media_type='application/json')

    return JSONResponse([raw_text_query.query, results],
                        media_type='application/x-suggestions+json')


@app.route('/preferences', methods=['GET', 'POST'])
async def preferences(request):
    """Render preferences page && save user preferences"""

    await pre_request(request)
    preferences = request.state.preferences

    # save preferences
    if request.method == 'POST':
        resp = RedirectResponse(request.url_for('index'))
        for cookie_name in request.cookies:
            resp.delete_cookie(cookie_name)
        return preferences.save(resp)

    # stats for preferences page
    stats = {}

    engines_by_category = {}
    for c in categories:
        engines_by_category[c] = []
        for e in categories[c]:
            if not preferences.validate_token(e):
                continue

            stats[e.name] = {'time': None,
                             'warn_timeout': False,
                             'warn_time': False}
            if e.timeout > settings['outgoing']['request_timeout']:
                stats[e.name]['warn_timeout'] = True
            stats[e.name]['supports_selected_language'] = _is_selected_language_supported(e, preferences)

            engines_by_category[c].append(e)

    # get first element [0], the engine time,
    # and then the second element [1] : the time (the first one is the label)
    for engine_stat in get_engines_stats(preferences)[0][1]:
        stats[engine_stat.get('name')]['time'] = round(engine_stat.get('avg'), 3)
        if engine_stat.get('avg') > settings['outgoing']['request_timeout']:
            stats[engine_stat.get('name')]['warn_time'] = True
    # end of stats

    locked_preferences = list()
    if 'preferences' in settings and 'lock' in settings['preferences']:
        locked_preferences = settings['preferences']['lock']

    return render(request,
                  'preferences.html',
                  selected_categories=get_selected_categories(preferences, request.state.form),
                  all_categories=_get_ordered_categories(),
                  locales=settings['locales'],
                  current_locale=preferences.get_value("locale"),
                  image_proxy=preferences.get_value('image_proxy'),
                  engines_by_category=engines_by_category,
                  stats=stats,
                  answerers=[{'info': a.self_info(), 'keywords': a.keywords} for a in answerers],
                  disabled_engines=preferences.engines.get_disabled(),
                  allowed_plugins=preferences.plugins.get_enabled(),
                  autocomplete_backends=autocomplete_backends,
                  shortcuts={y: x for x, y in engine_shortcuts.items()},
                  themes=themes,
                  plugins=plugins,
                  doi_resolvers=settings['doi_resolvers'],
                  current_doi_resolver=get_doi_resolver(request.state.form, preferences.get_value('doi_resolver')),
                  theme=get_current_theme_name(request),
                  preferences_url_params=preferences.get_as_url_params(),
                  base_url=get_base_url(request),
                  locked_preferences=locked_preferences,
                  preferences=True)


def _is_selected_language_supported(engine, preferences):
    language = preferences.get_value('language')
    return (language == 'all'
            or match_language(language,
                              getattr(engine, 'supported_languages', []),
                              getattr(engine, 'language_aliases', {}), None))


@app.route('/about', methods=['GET'])
async def about(request):
    """Render about page"""
    await pre_request(request)
    return render(request,
                  'about.html')


@app.route('/config', methods=['GET'])
async def config(request):
    """Return configuration in JSON format."""
    await pre_request(request)
    _engines = []
    for name, engine in engines.items():
        if not request.state.preferences.validate_token(engine):
            continue

        supported_languages = engine.supported_languages
        if isinstance(engine.supported_languages, dict):
            supported_languages = list(engine.supported_languages.keys())

        _engines.append({
            'name': name,
            'categories': engine.categories,
            'shortcut': engine.shortcut,
            'enabled': not engine.disabled,
            'paging': engine.paging,
            'language_support': engine.language_support,
            'supported_languages': supported_languages,
            'safesearch': engine.safesearch,
            'time_range_support': engine.time_range_support,
            'timeout': engine.timeout
        })

    _plugins = []
    for _ in plugins:
        _plugins.append({'name': _.name, 'enabled': _.default_on})

    return JSONResponse({
        'categories': list(categories.keys()),
        'engines': _engines,
        'plugins': _plugins,
        'instance_name': settings['general']['instance_name'],
        'locales': settings['locales'],
        'default_locale': settings['ui']['default_locale'],
        'autocomplete': settings['search']['autocomplete'],
        'safe_search': settings['search']['safe_search'],
        'default_theme': settings['ui']['default_theme'],
        'version': VERSION_STRING,
        'brand': {
            'GIT_URL': brand.GIT_URL,
            'DOCS_URL': brand.DOCS_URL
        },
        'doi_resolvers': [r for r in settings['doi_resolvers']],
        'default_doi_resolver': settings['default_doi_resolver'],
    })


@app.route('/clear_cookies')
async def clear_cookies(request):
    resp = RedirectResponse(request.url_for('index'))
    for cookie_name in request.cookies:
        resp.delete_cookie(cookie_name)
    return resp


@app.route('/opensearch.xml', methods=['GET'])
async def opensearch(request):
    await pre_request(request)

    method = 'post'

    if request.state.preferences.get_value('method') == 'GET':
        method = 'get'

    # chrome/chromium only supports HTTP GET....
    if request.headers.get('User-Agent', '').lower().find('webkit') >= 0:
        method = 'get'

    return render(request,
                  'opensearch.xml',
                  mimetype="application/opensearchdescription+xml",
                  opensearch_method=method,
                  host=get_base_url(request),
                  urljoin=urljoin,
                  override_theme='__common__')


@app.route('/favicon.ico')
async def favicon(request):
    await pre_request(request)
    file_path = os.path.join(static_path, 'themes', get_current_theme_name(request), 'img', 'favicon.png')
    return FileResponse(file_path,
                        media_type='image/vnd.microsoft.icon')


@app.route('/js_translations')
async def js_translations(request):
    await pre_request(request)
    return render(request,
                  'translations.js.tpl',
                  override_theme='__common__',
                  media_type='text/javascript')


@app.route('/stats', methods=['GET'])
async def stats(request):
    """Render engine statistics page."""
    await pre_request(request)
    stats = get_engines_stats(request.state.preferences)
    return render(request,
                  'stats.html',
                  stats=stats)


@app.route('/robots.txt', methods=['GET'])
async def robots():
    return PlainTextResponse("""User-agent: *
Allow: /
Allow: /about
Disallow: /stats
Disallow: /preferences
Disallow: /*?*q=*
""", media_type='text/plain')


@app.route('/image_proxy', methods=['GET'])
async def image_proxy(request):
    global client

    url = request.query_params.get('url')

    if not url:
        return PlainTextResponse('', status_code=400)

    if not check_hmac_for_url(url.encode(), request.query_params.get('h')):
        return PlainTextResponse('', status_code=400)

    headers = dict_subset(request.headers, {'If-Modified-Since', 'If-None-Match'})
    headers['User-Agent'] = gen_useragent()

    httpx_req = client.build_request("GET", url, headers=headers)
    response = await client.send(httpx_req, stream=True)

    if response.status_code == 304:
        return PlainTextResponse('', status_code=304)

    if response.status_code != 200:
        logger.debug('image-proxy: wrong response code: {0}'.format(response.status_code))
        if response.status_code >= 400:
            return PlainTextResponse('', status_code=response.status_code)
        return PlainTextResponse('', status_code=400)

    if not response.headers.get('content-type', '').startswith('image/'):
        logger.debug('image-proxy: wrong content-type: {0}'.format(response.headers.get('content-type')))
        return PlainTextResponse('', status_code=400)

    headers = dict_subset(response.headers, {'Content-Length', 'Length', 'Date', 'Last-Modified', 'Expires', 'Etag'})
    return StreamingResponse(response.aiter_bytes(),
                             media_type=response.headers['content-type'],
                             headers=headers,
                             background=BackgroundTask(response.aclose))


def main():
    kwargs = {
        'loop': 'uvloop',
        'ws': 'none',
        'http': 'httptools',
        'host': settings.get('server', {}).get('bind_address', 8888),
        'port': settings.get('server', {}).get('port', 8888),
    }

    headers = settings.get('server', {}).get('default_http_headers', None)
    if isinstance(headers, dict):
        kwargs['headers'] = list(headers.items())

    base_url = settings.get('server', {}).get('base_url', None)
    if base_url:
        kwargs['proxy_headers'] = True
        kwargs['root_path'] = base_url

    if searx_debug:
        # debug: enable uvicorn reload
        kwargs['reload'] = True
    else:
        # not really production
        # see https://www.uvicorn.org/deployment/#using-a-process-manager
        kwargs['workers'] = os.cpu_count()
    uvicorn.run('searx.web.__main__:app', **kwargs)


if __name__ == '__main__':
    main()
