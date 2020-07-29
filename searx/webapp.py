#!/usr/bin/env python

'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2013- by Adam Tauber, <asciimoo@gmail.com>
'''

if __name__ == '__main__':
    from sys import path
    from os.path import realpath, dirname
    path.append(realpath(dirname(realpath(__file__)) + '/../'))

import hashlib
import hmac
import json
import os
import sys

import requests

from searx import logger
logger = logger.getChild('webapp')

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
except:
    logger.critical("cannot import dependency: pygments")
    from sys import exit
    exit(1)
try:
    from cgi import escape
except:
    from html import escape
from six import next
from datetime import datetime, timedelta
from time import time
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import (
    Flask, request, render_template, url_for, Response, make_response,
    redirect, send_from_directory
)
from babel.support import Translations
import flask_babel
from flask_babel import Babel, gettext, format_date, format_decimal
from flask.ctx import has_request_context
from flask.json import jsonify
from searx import brand, static_path
from searx import settings, searx_dir, searx_debug
from searx.exceptions import SearxParameterException
from searx.engines import (
    categories, engines, engine_shortcuts, get_engines_stats, initialize_engines
)
from searx.utils import (
    UnicodeWriter, highlight_content, html_to_text, get_resources_directory,
    get_static_files, get_result_templates, get_themes, gen_useragent,
    dict_subset, prettify_url, match_language
)
from searx.version import VERSION_STRING
from searx.languages import language_codes as languages
from searx.search import SearchWithPlugins, get_search_query_from_webapp
from searx.query import RawTextQuery
from searx.autocomplete import searx_bang, backends as autocomplete_backends
from searx.plugins import plugins
from searx.plugins.oa_doi_rewrite import get_doi_resolver
from searx.preferences import Preferences, ValidationException, LANGUAGE_CODES
from searx.answerers import answerers
from searx.url_utils import urlencode, urlparse, urljoin
from searx.utils import new_hmac

# check if the pyopenssl package is installed.
# It is needed for SSL connection without trouble, see #298
try:
    import OpenSSL.SSL  # NOQA
except ImportError:
    logger.critical("The pyopenssl package has to be installed.\n"
                    "Some HTTPS connections will fail")

try:
    from cStringIO import StringIO
except:
    from io import StringIO


if sys.version_info[0] == 3:
    unicode = str
    PY3 = True
else:
    logger.warning('\033[1;31m Python2 is no longer supported\033[0m')
    exit(1)

# serve pages with HTTP/1.1
from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.protocol_version = "HTTP/{}".format(settings['server'].get('http_protocol_version', '1.0'))

# about static
static_path = get_resources_directory(searx_dir, 'static', settings['ui']['static_path'])
logger.debug('static directory is %s', static_path)
static_files = get_static_files(static_path)

# about templates
default_theme = settings['ui']['default_theme']
templates_path = get_resources_directory(searx_dir, 'templates', settings['ui']['templates_path'])
logger.debug('templates directory is %s', templates_path)
themes = get_themes(templates_path)
result_templates = get_result_templates(templates_path)
global_favicons = []
for indice, theme in enumerate(themes):
    global_favicons.append([])
    theme_img_path = os.path.join(static_path, 'themes', theme, 'img', 'icons')
    for (dirpath, dirnames, filenames) in os.walk(theme_img_path):
        global_favicons[indice].extend(filenames)

# Flask app
app = Flask(
    __name__,
    static_folder=static_path,
    template_folder=templates_path
)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.secret_key = settings['server']['secret_key']

if not searx_debug \
   or os.environ.get("WERKZEUG_RUN_MAIN") == "true" \
   or os.environ.get('UWSGI_ORIGINAL_PROC_NAME') is not None:
    initialize_engines(settings['engines'])

babel = Babel(app)

rtl_locales = ['ar', 'arc', 'bcc', 'bqi', 'ckb', 'dv', 'fa', 'fa_IR', 'glk', 'he',
               'ku', 'mzn', 'pnb', 'ps', 'sd', 'ug', 'ur', 'yi']

# used when translating category names
_category_names = (gettext('files'),
                   gettext('general'),
                   gettext('music'),
                   gettext('social media'),
                   gettext('images'),
                   gettext('videos'),
                   gettext('it'),
                   gettext('news'),
                   gettext('map'),
                   gettext('science'))

outgoing_proxies = settings['outgoing'].get('proxies') or None

_flask_babel_get_translations = flask_babel.get_translations


# monkey patch for flask_babel.get_translations
def _get_translations():
    if has_request_context() and request.form.get('use-translation') == 'oc':
        babel_ext = flask_babel.current_app.extensions['babel']
        return Translations.load(next(babel_ext.translation_directories), 'oc')

    return _flask_babel_get_translations()


flask_babel.get_translations = _get_translations


def _get_browser_language(request, lang_list):
    for lang in request.headers.get("Accept-Language", "en").split(","):
        if ';' in lang:
            lang = lang.split(';')[0]
        locale = match_language(lang, lang_list, fallback=None)
        if locale is not None:
            return locale
    return settings['search']['default_lang'] or 'en'


@babel.localeselector
def get_locale():
    locale = _get_browser_language(request, settings['locales'].keys())

    logger.debug("default locale from browser info is `%s`", locale)

    if request.preferences.get_value('locale') != '':
        locale = request.preferences.get_value('locale')

    if 'locale' in request.form\
       and request.form['locale'] in settings['locales']:
        locale = request.form['locale']

    if locale == 'zh_TW':
        locale = 'zh_Hant_TW'

    if locale == 'oc':
        request.form['use-translation'] = 'oc'
        locale = 'fr_FR'

    logger.debug("selected locale is `%s`", locale)

    return locale


# code-highlighter
@app.template_filter('code_highlighter')
def code_highlighter(codelines, language=None):
    if not language:
        language = 'text'

    try:
        # find lexer by programing language
        lexer = get_lexer_by_name(language, stripall=True)
    except:
        # if lexer is not found, using default one
        logger.debug('highlighter cannot find lexer for {0}'.format(language))
        lexer = get_lexer_by_name('text', stripall=True)

    html_code = ''
    tmp_code = ''
    last_line = None

    # parse lines
    for line, code in codelines:
        if not last_line:
            line_code_start = line

        # new codeblock is detected
        if last_line is not None and\
           last_line + 1 != line:

            # highlight last codepart
            formatter = HtmlFormatter(linenos='inline',
                                      linenostart=line_code_start)
            html_code = html_code + highlight(tmp_code, lexer, formatter)

            # reset conditions for next codepart
            tmp_code = ''
            line_code_start = line

        # add codepart
        tmp_code += code + '\n'

        # update line
        last_line = line

    # highlight last codepart
    formatter = HtmlFormatter(linenos='inline', linenostart=line_code_start)
    html_code = html_code + highlight(tmp_code, lexer, formatter)

    return html_code


# Extract domain from url
@app.template_filter('extract_domain')
def extract_domain(url):
    return urlparse(url)[1]


def get_base_url():
    if settings['server']['base_url']:
        hostname = settings['server']['base_url']
    else:
        scheme = 'http'
        if request.is_secure:
            scheme = 'https'
        hostname = url_for('index', _external=True, _scheme=scheme)
    return hostname


def get_current_theme_name(override=None):
    """Returns theme name.

    Checks in this order:
    1. override
    2. cookies
    3. settings"""

    if override and (override in themes or override == '__common__'):
        return override
    theme_name = request.args.get('theme', request.preferences.get_value('theme'))
    if theme_name not in themes:
        theme_name = default_theme
    return theme_name


def get_result_template(theme, template_name):
    themed_path = theme + '/result_templates/' + template_name
    if themed_path in result_templates:
        return themed_path
    return 'result_templates/' + template_name


def url_for_theme(endpoint, override_theme=None, **values):
    if endpoint == 'static' and values.get('filename'):
        theme_name = get_current_theme_name(override=override_theme)
        filename_with_theme = "themes/{}/{}".format(theme_name, values['filename'])
        if filename_with_theme in static_files:
            values['filename'] = filename_with_theme
    return url_for(endpoint, **values)


def proxify(url):
    if url.startswith('//'):
        url = 'https:' + url

    if not settings.get('result_proxy'):
        return url

    url_params = dict(mortyurl=url.encode('utf-8'))

    if settings['result_proxy'].get('key'):
        url_params['mortyhash'] = hmac.new(settings['result_proxy']['key'],
                                           url.encode('utf-8'),
                                           hashlib.sha256).hexdigest()

    return '{0}?{1}'.format(settings['result_proxy']['url'],
                            urlencode(url_params))


def image_proxify(url):

    if url.startswith('//'):
        url = 'https:' + url

    if not request.preferences.get_value('image_proxy'):
        return url

    if url.startswith('data:image/'):
        # 50 is an arbitrary number to get only the beginning of the image.
        partial_base64 = url[len('data:image/'):50].split(';')
        if len(partial_base64) == 2 \
           and partial_base64[0] in ['gif', 'png', 'jpeg', 'pjpeg', 'webp', 'tiff', 'bmp']\
           and partial_base64[1].startswith('base64,'):
            return url
        else:
            return None

    if settings.get('result_proxy'):
        return proxify(url)

    h = new_hmac(settings['server']['secret_key'], url.encode('utf-8'))

    return '{0}?{1}'.format(url_for('image_proxy'),
                            urlencode(dict(url=url.encode('utf-8'), h=h)))


def render(template_name, override_theme=None, **kwargs):
    disabled_engines = request.preferences.engines.get_disabled()

    enabled_categories = set(category for engine_name in engines
                             for category in engines[engine_name].categories
                             if (engine_name, category) not in disabled_engines)

    if 'categories' not in kwargs:
        kwargs['categories'] = [x for x in
                                _get_ordered_categories()
                                if x in enabled_categories]

    if 'all_categories' not in kwargs:
        kwargs['all_categories'] = _get_ordered_categories()

    if 'selected_categories' not in kwargs:
        kwargs['selected_categories'] = []
        for arg in request.args:
            if arg.startswith('category_'):
                c = arg.split('_', 1)[1]
                if c in categories:
                    kwargs['selected_categories'].append(c)

    if not kwargs['selected_categories']:
        cookie_categories = request.preferences.get_value('categories')
        for ccateg in cookie_categories:
            kwargs['selected_categories'].append(ccateg)

    if not kwargs['selected_categories']:
        kwargs['selected_categories'] = ['general']

    if 'autocomplete' not in kwargs:
        kwargs['autocomplete'] = request.preferences.get_value('autocomplete')

    locale = request.preferences.get_value('locale')

    if locale in rtl_locales and 'rtl' not in kwargs:
        kwargs['rtl'] = True

    kwargs['searx_version'] = VERSION_STRING

    kwargs['method'] = request.preferences.get_value('method')

    kwargs['safesearch'] = str(request.preferences.get_value('safesearch'))

    kwargs['language_codes'] = languages
    if 'current_language' not in kwargs:
        kwargs['current_language'] = match_language(request.preferences.get_value('language'),
                                                    LANGUAGE_CODES)

    # override url_for function in templates
    kwargs['url_for'] = url_for_theme

    kwargs['image_proxify'] = image_proxify

    kwargs['proxify'] = proxify if settings.get('result_proxy', {}).get('url') else None

    kwargs['get_result_template'] = get_result_template

    kwargs['theme'] = get_current_theme_name(override=override_theme)

    kwargs['template_name'] = template_name

    kwargs['cookies'] = request.cookies

    kwargs['errors'] = request.errors

    kwargs['instance_name'] = settings['general']['instance_name']

    kwargs['results_on_new_tab'] = request.preferences.get_value('results_on_new_tab')

    kwargs['unicode'] = unicode

    kwargs['preferences'] = request.preferences

    kwargs['brand'] = brand

    kwargs['scripts'] = set()
    kwargs['endpoint'] = 'results' if 'q' in kwargs else request.endpoint
    for plugin in request.user_plugins:
        for script in plugin.js_dependencies:
            kwargs['scripts'].add(script)

    kwargs['styles'] = set()
    for plugin in request.user_plugins:
        for css in plugin.css_dependencies:
            kwargs['styles'].add(css)

    return render_template(
        '{}/{}'.format(kwargs['theme'], template_name), **kwargs)


def _get_ordered_categories():
    ordered_categories = []
    if 'categories_order' not in settings['ui']:
        ordered_categories = ['general']
        ordered_categories.extend(x for x in sorted(categories.keys()) if x != 'general')
        return ordered_categories
    ordered_categories = settings['ui']['categories_order']
    ordered_categories.extend(x for x in sorted(categories.keys()) if x not in ordered_categories)
    return ordered_categories


@app.before_request
def pre_request():
    request.start_time = time()
    request.timings = []
    request.errors = []

    preferences = Preferences(themes, list(categories.keys()), engines, plugins)
    request.preferences = preferences
    try:
        preferences.parse_dict(request.cookies)
    except:
        request.errors.append(gettext('Invalid settings, please edit your preferences'))

    # merge GET, POST vars
    # request.form
    request.form = dict(request.form.items())
    for k, v in request.args.items():
        if k not in request.form:
            request.form[k] = v

    if request.form.get('preferences'):
        preferences.parse_encoded_data(request.form['preferences'])
    else:
        try:
            preferences.parse_dict(request.form)
        except Exception as e:
            logger.exception('invalid settings')
            request.errors.append(gettext('Invalid settings'))

    # init search language and locale
    if not preferences.get_value("language"):
        preferences.parse_dict({"language": _get_browser_language(request, LANGUAGE_CODES)})
    if not preferences.get_value("locale"):
        preferences.parse_dict({"locale": get_locale()})

    # request.user_plugins
    request.user_plugins = []
    allowed_plugins = preferences.plugins.get_enabled()
    disabled_plugins = preferences.plugins.get_disabled()
    for plugin in plugins:
        if ((plugin.default_on and plugin.id not in disabled_plugins)
                or plugin.id in allowed_plugins):
            request.user_plugins.append(plugin)


@app.after_request
def post_request(response):
    total_time = time() - request.start_time
    timings_all = ['total;dur=' + str(round(total_time * 1000, 3))]
    if len(request.timings) > 0:
        timings = sorted(request.timings, key=lambda v: v['total'])
        timings_total = ['total_' + str(i) + '_' + v['engine'] +
                         ';dur=' + str(round(v['total'] * 1000, 3)) for i, v in enumerate(timings)]
        timings_load = ['load_' + str(i) + '_' + v['engine'] +
                        ';dur=' + str(round(v['load'] * 1000, 3)) for i, v in enumerate(timings)]
        timings_all = timings_all + timings_total + timings_load
    response.headers.add('Server-Timing', ', '.join(timings_all))
    return response


def index_error(output_format, error_message):
    if output_format == 'json':
        return Response(json.dumps({'error': error_message}),
                        mimetype='application/json')
    elif output_format == 'csv':
        response = Response('', mimetype='application/csv')
        cont_disp = 'attachment;Filename=searx.csv'
        response.headers.add('Content-Disposition', cont_disp)
        return response
    elif output_format == 'rss':
        response_rss = render(
            'opensearch_response_rss.xml',
            results=[],
            q=request.form['q'] if 'q' in request.form else '',
            number_of_results=0,
            base_url=get_base_url(),
            error_message=error_message,
            override_theme='__common__',
        )
        return Response(response_rss, mimetype='text/xml')
    else:
        # html
        request.errors.append(gettext('search error'))
        return render(
            'index.html',
        )


@app.route('/search', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    """Render index page.

    Supported outputs: html, json, csv, rss.
    """

    # output_format
    output_format = request.form.get('format', 'html')
    if output_format not in ['html', 'csv', 'json', 'rss']:
        output_format = 'html'

    # check if there is query
    if request.form.get('q') is None:
        if output_format == 'html':
            return render(
                'index.html',
            )
        else:
            return index_error(output_format, 'No query'), 400

    # search
    search_query = None
    raw_text_query = None
    result_container = None
    try:
        search_query, raw_text_query = get_search_query_from_webapp(request.preferences, request.form)
        # search = Search(search_query) #  without plugins
        search = SearchWithPlugins(search_query, request.user_plugins, request)

        result_container = search.search()

    except Exception as e:
        # log exception
        logger.exception('search error')

        # is it an invalid input parameter or something else ?
        if (issubclass(e.__class__, SearxParameterException)):
            return index_error(output_format, e.message), 400
        else:
            return index_error(output_format, gettext('search error')), 500

    # results
    results = result_container.get_ordered_results()
    number_of_results = result_container.results_number()
    if number_of_results < result_container.results_length():
        number_of_results = 0

    # checkin for a external bang
    if result_container.redirect_url:
        return redirect(result_container.redirect_url)

    # UI
    advanced_search = request.form.get('advanced_search', None)

    # Server-Timing header
    request.timings = result_container.get_timings()

    # output
    for result in results:
        if output_format == 'html':
            if 'content' in result and result['content']:
                result['content'] = highlight_content(escape(result['content'][:1024]), search_query.query)
            if 'title' in result and result['title']:
                result['title'] = highlight_content(escape(result['title'] or u''), search_query.query)
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
                        result['publishedDate'] = gettext(u'{minutes} minute(s) ago').format(minutes=minutes)
                    else:
                        result['publishedDate'] = gettext(u'{hours} hour(s), {minutes} minute(s) ago').format(hours=hours, minutes=minutes)  # noqa
                else:
                    result['publishedDate'] = format_date(result['publishedDate'])

    if output_format == 'json':
        return Response(json.dumps({'query': search_query.query.decode('utf-8'),
                                    'number_of_results': number_of_results,
                                    'results': results,
                                    'answers': list(result_container.answers),
                                    'corrections': list(result_container.corrections),
                                    'infoboxes': result_container.infoboxes,
                                    'suggestions': list(result_container.suggestions),
                                    'unresponsive_engines': __get_translated_errors(result_container.unresponsive_engines)},  # noqa
                                   default=lambda item: list(item) if isinstance(item, set) else item),
                        mimetype='application/json')
    elif output_format == 'csv':
        csv = UnicodeWriter(StringIO())
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
        response = Response(csv.stream.read(), mimetype='application/csv')
        cont_disp = 'attachment;Filename=searx_-_{0}.csv'.format(search_query.query.decode('utf-8'))
        response.headers.add('Content-Disposition', cont_disp)
        return response

    elif output_format == 'rss':
        response_rss = render(
            'opensearch_response_rss.xml',
            results=results,
            answers=result_container.answers,
            corrections=result_container.corrections,
            suggestions=result_container.suggestions,
            q=request.form['q'],
            number_of_results=number_of_results,
            base_url=get_base_url(),
            override_theme='__common__',
        )
        return Response(response_rss, mimetype='text/xml')

    # HTML output format

    # suggestions: use RawTextQuery to get the suggestion URLs with the same bang
    suggestion_urls = list(map(lambda suggestion: {
                               'url': raw_text_query.changeSearchQuery(suggestion).getFullQuery(),
                               'title': suggestion
                               },
                               result_container.suggestions))

    correction_urls = list(map(lambda correction: {
                               'url': raw_text_query.changeSearchQuery(correction).getFullQuery(),
                               'title': correction
                               },
                               result_container.corrections))
    #
    return render(
        'results.html',
        results=results,
        q=request.form['q'],
        selected_categories=search_query.categories,
        pageno=search_query.pageno,
        time_range=search_query.time_range,
        number_of_results=format_decimal(number_of_results),
        advanced_search=advanced_search,
        suggestions=suggestion_urls,
        answers=result_container.answers,
        corrections=correction_urls,
        infoboxes=result_container.infoboxes,
        paging=result_container.paging,
        unresponsive_engines=__get_translated_errors(result_container.unresponsive_engines),
        current_language=match_language(search_query.lang,
                                        LANGUAGE_CODES,
                                        fallback=request.preferences.get_value("language")),
        base_url=get_base_url(),
        theme=get_current_theme_name(),
        favicons=global_favicons[themes.index(get_current_theme_name())],
        timeout_limit=request.form.get('timeout_limit', None)
    )


def __get_translated_errors(unresponsive_engines):
    translated_errors = []
    for unresponsive_engine in unresponsive_engines:
        error_msg = gettext(unresponsive_engine[1])
        if unresponsive_engine[2]:
            error_msg = "{} {}".format(error_msg, unresponsive_engine[2])
        translated_errors.append((unresponsive_engine[0], error_msg))
    return translated_errors


@app.route('/about', methods=['GET'])
def about():
    """Render about page"""
    return render(
        'about.html',
    )


@app.route('/autocompleter', methods=['GET', 'POST'])
def autocompleter():
    """Return autocompleter results"""

    # set blocked engines
    disabled_engines = request.preferences.engines.get_disabled()

    # parse query
    if PY3:
        raw_text_query = RawTextQuery(request.form.get('q', b''), disabled_engines)
    else:
        raw_text_query = RawTextQuery(request.form.get('q', u'').encode('utf-8'), disabled_engines)
    raw_text_query.parse_query()

    # check if search query is set
    if not raw_text_query.getSearchQuery():
        return '', 400

    # run autocompleter
    completer = autocomplete_backends.get(request.preferences.get_value('autocomplete'))

    # parse searx specific autocompleter results like !bang
    raw_results = searx_bang(raw_text_query)

    # normal autocompletion results only appear if no inner results returned
    # and there is a query part besides the engine and language bangs
    if len(raw_results) == 0 and completer and (len(raw_text_query.query_parts) > 1 or
                                                (len(raw_text_query.languages) == 0 and
                                                 not raw_text_query.specific)):
        # get language from cookie
        language = request.preferences.get_value('language')
        if not language or language == 'all':
            language = 'en'
        else:
            language = language.split('-')[0]
        # run autocompletion
        raw_results.extend(completer(raw_text_query.getSearchQuery(), language))

    # parse results (write :language and !engine back to result string)
    results = []
    for result in raw_results:
        raw_text_query.changeSearchQuery(result)

        # add parsed result
        results.append(raw_text_query.getFullQuery())

    # return autocompleter results
    if request.form.get('format') == 'x-suggestions':
        return Response(json.dumps([raw_text_query.query, results]),
                        mimetype='application/json')

    return Response(json.dumps(results),
                    mimetype='application/json')


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    """Render preferences page && save user preferences"""

    # save preferences
    if request.method == 'POST':
        resp = make_response(redirect(urljoin(settings['server']['base_url'], url_for('index'))))
        try:
            request.preferences.parse_form(request.form)
        except ValidationException:
            request.errors.append(gettext('Invalid settings, please edit your preferences'))
            return resp
        return request.preferences.save(resp)

    # render preferences
    image_proxy = request.preferences.get_value('image_proxy')
    lang = request.preferences.get_value('language')
    disabled_engines = request.preferences.engines.get_disabled()
    allowed_plugins = request.preferences.plugins.get_enabled()

    # stats for preferences page
    stats = {}

    engines_by_category = {}
    for c in categories:
        engines_by_category[c] = []
        for e in categories[c]:
            if not request.preferences.validate_token(e):
                continue

            stats[e.name] = {'time': None,
                             'warn_timeout': False,
                             'warn_time': False}
            if e.timeout > settings['outgoing']['request_timeout']:
                stats[e.name]['warn_timeout'] = True
            stats[e.name]['supports_selected_language'] = _is_selected_language_supported(e, request.preferences)

            engines_by_category[c].append(e)

    # get first element [0], the engine time,
    # and then the second element [1] : the time (the first one is the label)
    for engine_stat in get_engines_stats(request.preferences)[0][1]:
        stats[engine_stat.get('name')]['time'] = round(engine_stat.get('avg'), 3)
        if engine_stat.get('avg') > settings['outgoing']['request_timeout']:
            stats[engine_stat.get('name')]['warn_time'] = True
    # end of stats

    return render('preferences.html',
                  locales=settings['locales'],
                  current_locale=request.preferences.get_value("locale"),
                  image_proxy=image_proxy,
                  engines_by_category=engines_by_category,
                  stats=stats,
                  answerers=[{'info': a.self_info(), 'keywords': a.keywords} for a in answerers],
                  disabled_engines=disabled_engines,
                  autocomplete_backends=autocomplete_backends,
                  shortcuts={y: x for x, y in engine_shortcuts.items()},
                  themes=themes,
                  plugins=plugins,
                  doi_resolvers=settings['doi_resolvers'],
                  current_doi_resolver=get_doi_resolver(request.args, request.preferences.get_value('doi_resolver')),
                  allowed_plugins=allowed_plugins,
                  theme=get_current_theme_name(),
                  preferences_url_params=request.preferences.get_as_url_params(),
                  base_url=get_base_url(),
                  preferences=True)


def _is_selected_language_supported(engine, preferences):
    language = preferences.get_value('language')
    return (language == 'all'
            or match_language(language,
                              getattr(engine, 'supported_languages', []),
                              getattr(engine, 'language_aliases', {}), None))


@app.route('/image_proxy', methods=['GET'])
def image_proxy():
    url = request.args.get('url').encode('utf-8')

    if not url:
        return '', 400

    h = new_hmac(settings['server']['secret_key'], url)

    if h != request.args.get('h'):
        return '', 400

    headers = dict_subset(request.headers, {'If-Modified-Since', 'If-None-Match'})
    headers['User-Agent'] = gen_useragent()

    resp = requests.get(url,
                        stream=True,
                        timeout=settings['outgoing']['request_timeout'],
                        headers=headers,
                        proxies=outgoing_proxies)

    if resp.status_code == 304:
        return '', resp.status_code

    if resp.status_code != 200:
        logger.debug('image-proxy: wrong response code: {0}'.format(resp.status_code))
        if resp.status_code >= 400:
            return '', resp.status_code
        return '', 400

    if not resp.headers.get('content-type', '').startswith('image/'):
        logger.debug('image-proxy: wrong content-type: {0}'.format(resp.headers.get('content-type')))
        return '', 400

    img = b''
    chunk_counter = 0

    for chunk in resp.iter_content(1024 * 1024):
        chunk_counter += 1
        if chunk_counter > 5:
            return '', 502  # Bad gateway - file is too big (>5M)
        img += chunk

    headers = dict_subset(resp.headers, {'Content-Length', 'Length', 'Date', 'Last-Modified', 'Expires', 'Etag'})

    return Response(img, mimetype=resp.headers['content-type'], headers=headers)


@app.route('/stats', methods=['GET'])
def stats():
    """Render engine statistics page."""
    stats = get_engines_stats(request.preferences)
    return render(
        'stats.html',
        stats=stats,
    )


@app.route('/robots.txt', methods=['GET'])
def robots():
    return Response("""User-agent: *
Allow: /
Allow: /about
Disallow: /stats
Disallow: /preferences
Disallow: /*?*q=*
""", mimetype='text/plain')


@app.route('/opensearch.xml', methods=['GET'])
def opensearch():
    method = 'post'

    if request.preferences.get_value('method') == 'GET':
        method = 'get'

    # chrome/chromium only supports HTTP GET....
    if request.headers.get('User-Agent', '').lower().find('webkit') >= 0:
        method = 'get'

    ret = render('opensearch.xml',
                 opensearch_method=method,
                 host=get_base_url(),
                 urljoin=urljoin,
                 override_theme='__common__')

    resp = Response(response=ret,
                    status=200,
                    mimetype="application/opensearchdescription+xml")
    return resp


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path,
                                            static_path,
                                            'themes',
                                            get_current_theme_name(),
                                            'img'),
                               'favicon.png',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/clear_cookies')
def clear_cookies():
    resp = make_response(redirect(urljoin(settings['server']['base_url'], url_for('index'))))
    for cookie_name in request.cookies:
        resp.delete_cookie(cookie_name)
    return resp


@app.route('/config')
def config():
    """Return configuration in JSON format."""
    _engines = []
    for name, engine in engines.items():
        if not request.preferences.validate_token(engine):
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

    return jsonify({
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


@app.route('/translations.js')
def js_translations():
    return render(
        'translations.js.tpl',
        override_theme='__common__',
    ), {'Content-Type': 'text/javascript; charset=UTF-8'}


@app.errorhandler(404)
def page_not_found(e):
    return render('404.html'), 404


def run():
    logger.debug('starting webserver on %s:%s', settings['server']['bind_address'], settings['server']['port'])
    app.run(
        debug=searx_debug,
        use_debugger=searx_debug,
        port=settings['server']['port'],
        host=settings['server']['bind_address'],
        threaded=True
    )


class ReverseProxyPathFix(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    http://flask.pocoo.org/snippets/35/

    In nginx:
    location /myprefix {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


application = app
# patch app to handle non root url-s behind proxy & wsgi
app.wsgi_app = ReverseProxyPathFix(ProxyFix(application.wsgi_app))

if __name__ == "__main__":
    run()
