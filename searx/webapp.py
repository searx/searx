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

import json
import cStringIO
import os
import hashlib
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

from datetime import datetime, timedelta
from urllib import urlencode
from urlparse import urlparse
from werkzeug.contrib.fixers import ProxyFix
from flask import (
    Flask, request, render_template, url_for, Response, make_response,
    redirect, send_from_directory
)
from flask.ext.babel import Babel, gettext, format_date
from searx import settings, searx_dir
from searx.engines import (
    categories, engines, get_engines_stats, engine_shortcuts
)
from searx.utils import (
    UnicodeWriter, highlight_content, html_to_text, get_themes,
    get_static_files, get_result_templates, gen_useragent, dict_subset,
    prettify_url, get_blocked_engines
)
from searx.version import VERSION_STRING
from searx.languages import language_codes
from searx.search import Search
from searx.query import Query
from searx.autocomplete import searx_bang, backends as autocomplete_backends
from searx.plugins import plugins

# check if the pyopenssl, ndg-httpsclient, pyasn1 packages are installed.
# They are needed for SSL connection without trouble, see #298
try:
    import OpenSSL.SSL  # NOQA
    import ndg.httpsclient  # NOQA
    import pyasn1  # NOQA
except ImportError:
    logger.critical("The pyopenssl, ndg-httpsclient, pyasn1 packages have to be installed.\n"
                    "Some HTTPS connections will failed")


static_path, templates_path, themes =\
    get_themes(settings['ui']['themes_path']
               if settings['ui']['themes_path']
               else searx_dir)

default_theme = settings['ui']['default_theme']

static_files = get_static_files(searx_dir)

result_templates = get_result_templates(searx_dir)

app = Flask(
    __name__,
    static_folder=static_path,
    template_folder=templates_path
)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.secret_key = settings['server']['secret_key']

babel = Babel(app)

rtl_locales = ['ar', 'arc', 'bcc', 'bqi', 'ckb', 'dv', 'fa', 'glk', 'he',
               'ku', 'mzn', 'pnb'', ''ps', 'sd', 'ug', 'ur', 'yi']

global_favicons = []
for indice, theme in enumerate(themes):
    global_favicons.append([])
    theme_img_path = searx_dir + "/static/themes/" + theme + "/img/icons/"
    for (dirpath, dirnames, filenames) in os.walk(theme_img_path):
        global_favicons[indice].extend(filenames)

cookie_max_age = 60 * 60 * 24 * 365 * 5  # 5 years

_category_names = (gettext('files'),
                   gettext('general'),
                   gettext('music'),
                   gettext('social media'),
                   gettext('images'),
                   gettext('videos'),
                   gettext('it'),
                   gettext('news'),
                   gettext('map'))

outgoing_proxies = settings['outgoing'].get('proxies', None)


@babel.localeselector
def get_locale():
    locale = request.accept_languages.best_match(settings['locales'].keys())

    if settings['ui'].get('default_locale'):
        locale = settings['ui']['default_locale']

    if request.cookies.get('locale', '') in settings['locales']:
        locale = request.cookies.get('locale', '')

    if 'locale' in request.args\
       and request.args['locale'] in settings['locales']:
        locale = request.args['locale']

    if 'locale' in request.form\
       and request.form['locale'] in settings['locales']:
        locale = request.form['locale']

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

    if override and override in themes:
        return override
    theme_name = request.args.get('theme',
                                  request.cookies.get('theme',
                                                      default_theme))
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


def image_proxify(url):

    if url.startswith('//'):
        url = 'https:' + url

    if not settings['server'].get('image_proxy') and not request.cookies.get('image_proxy'):
        return url

    hash_string = url + settings['server']['secret_key']
    h = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

    return '{0}?{1}'.format(url_for('image_proxy'),
                            urlencode(dict(url=url.encode('utf-8'), h=h)))


def render(template_name, override_theme=None, **kwargs):
    blocked_engines = get_blocked_engines(engines, request.cookies)

    autocomplete = request.cookies.get('autocomplete', settings['search']['autocomplete'])

    if autocomplete not in autocomplete_backends:
        autocomplete = None

    nonblocked_categories = set(category for engine_name in engines
                                for category in engines[engine_name].categories
                                if (engine_name, category) not in blocked_engines)

    if 'categories' not in kwargs:
        kwargs['categories'] = ['general']
        kwargs['categories'].extend(x for x in
                                    sorted(categories.keys())
                                    if x != 'general'
                                    and x in nonblocked_categories)

    if 'all_categories' not in kwargs:
        kwargs['all_categories'] = ['general']
        kwargs['all_categories'].extend(x for x in
                                        sorted(categories.keys())
                                        if x != 'general')

    if 'selected_categories' not in kwargs:
        kwargs['selected_categories'] = []
        for arg in request.args:
            if arg.startswith('category_'):
                c = arg.split('_', 1)[1]
                if c in categories:
                    kwargs['selected_categories'].append(c)

    if not kwargs['selected_categories']:
        cookie_categories = request.cookies.get('categories', '').split(',')
        for ccateg in cookie_categories:
            if ccateg in categories:
                kwargs['selected_categories'].append(ccateg)

    if not kwargs['selected_categories']:
        kwargs['selected_categories'] = ['general']

    if 'autocomplete' not in kwargs:
        kwargs['autocomplete'] = autocomplete

    if get_locale() in rtl_locales and 'rtl' not in kwargs:
        kwargs['rtl'] = True

    kwargs['searx_version'] = VERSION_STRING

    kwargs['method'] = request.cookies.get('method', 'POST')

    kwargs['safesearch'] = request.cookies.get('safesearch', str(settings['search']['safe_search']))

    # override url_for function in templates
    kwargs['url_for'] = url_for_theme

    kwargs['image_proxify'] = image_proxify

    kwargs['get_result_template'] = get_result_template

    kwargs['theme'] = get_current_theme_name(override=override_theme)

    kwargs['template_name'] = template_name

    kwargs['cookies'] = request.cookies

    kwargs['scripts'] = set()
    for plugin in request.user_plugins:
        for script in plugin.js_dependencies:
            kwargs['scripts'].add(script)

    kwargs['styles'] = set()
    for plugin in request.user_plugins:
        for css in plugin.css_dependencies:
            kwargs['styles'].add(css)

    return render_template(
        '{}/{}'.format(kwargs['theme'], template_name), **kwargs)


@app.before_request
def pre_request():
    # merge GET, POST vars
    request.form = dict(request.form.items())
    for k, v in request.args.items():
        if k not in request.form:
            request.form[k] = v

    request.user_plugins = []
    allowed_plugins = request.cookies.get('allowed_plugins', '').split(',')
    disabled_plugins = request.cookies.get('disabled_plugins', '').split(',')
    for plugin in plugins:
        if ((plugin.default_on and plugin.id not in disabled_plugins)
                or plugin.id in allowed_plugins):
            request.user_plugins.append(plugin)


@app.route('/search', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    """Render index page.

    Supported outputs: html, json, csv, rss.
    """

    if not request.args and not request.form:
        return render(
            'index.html',
        )

    try:
        search = Search(request)
    except:
        return render(
            'index.html',
        )

    if plugins.call('pre_search', request, locals()):
        search.search(request)

    plugins.call('post_search', request, locals())

    for result in search.results:

        plugins.call('on_result', request, locals())
        if not search.paging and engines[result['engine']].paging:
            search.paging = True

        if search.request_data.get('format', 'html') == 'html':
            if 'content' in result:
                result['content'] = highlight_content(result['content'],
                                                      search.query.encode('utf-8'))  # noqa
            result['title'] = highlight_content(result['title'],
                                                search.query.encode('utf-8'))
        else:
            if result.get('content'):
                result['content'] = html_to_text(result['content']).strip()
            # removing html content and whitespace duplications
            result['title'] = ' '.join(html_to_text(result['title']).strip().split())

        result['pretty_url'] = prettify_url(result['url'])

        # TODO, check if timezone is calculated right
        if 'publishedDate' in result:
            result['pubdate'] = result['publishedDate'].strftime('%Y-%m-%d %H:%M:%S%z')
            if result['publishedDate'].replace(tzinfo=None) >= datetime.now() - timedelta(days=1):
                timedifference = datetime.now() - result['publishedDate'].replace(tzinfo=None)
                minutes = int((timedifference.seconds / 60) % 60)
                hours = int(timedifference.seconds / 60 / 60)
                if hours == 0:
                    result['publishedDate'] = gettext(u'{minutes} minute(s) ago').format(minutes=minutes)  # noqa
                else:
                    result['publishedDate'] = gettext(u'{hours} hour(s), {minutes} minute(s) ago').format(hours=hours, minutes=minutes)  # noqa
            else:
                result['publishedDate'] = format_date(result['publishedDate'])

    if search.request_data.get('format') == 'json':
        return Response(json.dumps({'query': search.query,
                                    'results': search.results}),
                        mimetype='application/json')
    elif search.request_data.get('format') == 'csv':
        csv = UnicodeWriter(cStringIO.StringIO())
        keys = ('title', 'url', 'content', 'host', 'engine', 'score')
        if search.results:
            csv.writerow(keys)
            for row in search.results:
                row['host'] = row['parsed_url'].netloc
                csv.writerow([row.get(key, '') for key in keys])
            csv.stream.seek(0)
        response = Response(csv.stream.read(), mimetype='application/csv')
        cont_disp = 'attachment;Filename=searx_-_{0}.csv'.format(search.query)
        response.headers.add('Content-Disposition', cont_disp)
        return response
    elif search.request_data.get('format') == 'rss':
        response_rss = render(
            'opensearch_response_rss.xml',
            results=search.results,
            q=search.request_data['q'],
            number_of_results=len(search.results),
            base_url=get_base_url()
        )
        return Response(response_rss, mimetype='text/xml')

    return render(
        'results.html',
        results=search.results,
        q=search.request_data['q'],
        selected_categories=search.categories,
        paging=search.paging,
        pageno=search.pageno,
        base_url=get_base_url(),
        suggestions=search.suggestions,
        answers=search.answers,
        infoboxes=search.infoboxes,
        theme=get_current_theme_name(),
        favicons=global_favicons[themes.index(get_current_theme_name())]
    )


@app.route('/about', methods=['GET'])
def about():
    """Render about page"""
    return render(
        'about.html',
    )


@app.route('/autocompleter', methods=['GET', 'POST'])
def autocompleter():
    """Return autocompleter results"""
    request_data = {}

    # select request method
    if request.method == 'POST':
        request_data = request.form
    else:
        request_data = request.args

    # set blocked engines
    blocked_engines = get_blocked_engines(engines, request.cookies)

    # parse query
    query = Query(request_data.get('q', '').encode('utf-8'), blocked_engines)
    query.parse_query()

    # check if search query is set
    if not query.getSearchQuery():
        return '', 400

    # run autocompleter
    completer = autocomplete_backends.get(request.cookies.get('autocomplete', settings['search']['autocomplete']))

    # parse searx specific autocompleter results like !bang
    raw_results = searx_bang(query)

    # normal autocompletion results only appear if max 3 inner results returned
    if len(raw_results) <= 3 and completer:
        # run autocompletion
        raw_results.extend(completer(query.getSearchQuery()))

    # parse results (write :language and !engine back to result string)
    results = []
    for result in raw_results:
        query.changeSearchQuery(result)

        # add parsed result
        results.append(query.getFullQuery())

    # return autocompleter results
    if request_data.get('format') == 'x-suggestions':
        return Response(json.dumps([query.query, results]),
                        mimetype='application/json')

    return Response(json.dumps(results),
                    mimetype='application/json')


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    """Render preferences page.

    Settings that are going to be saved as cookies."""
    lang = None
    image_proxy = request.cookies.get('image_proxy', settings['server'].get('image_proxy'))

    if request.cookies.get('language')\
       and request.cookies['language'] in (x[0] for x in language_codes):
        lang = request.cookies['language']

    blocked_engines = []

    resp = make_response(redirect(url_for('index')))

    if request.method == 'GET':
        blocked_engines = get_blocked_engines(engines, request.cookies)
    else:  # on save
        selected_categories = []
        post_disabled_plugins = []
        locale = None
        autocomplete = ''
        method = 'POST'
        safesearch = settings['search']['safe_search']
        for pd_name, pd in request.form.items():
            if pd_name.startswith('category_'):
                category = pd_name[9:]
                if category not in categories:
                    continue
                selected_categories.append(category)
            elif pd_name == 'locale' and pd in settings['locales']:
                locale = pd
            elif pd_name == 'image_proxy':
                image_proxy = pd
            elif pd_name == 'autocomplete':
                autocomplete = pd
            elif pd_name == 'language' and (pd == 'all' or
                                            pd in (x[0] for
                                                   x in language_codes)):
                lang = pd
            elif pd_name == 'method':
                method = pd
            elif pd_name == 'safesearch':
                safesearch = pd
            elif pd_name.startswith('engine_'):
                if pd_name.find('__') > -1:
                    # TODO fix underscore vs space
                    engine_name, category = [x.replace('_', ' ') for x in
                                             pd_name.replace('engine_', '', 1).split('__', 1)]
                    if engine_name in engines and category in engines[engine_name].categories:
                        blocked_engines.append((engine_name, category))
            elif pd_name == 'theme':
                theme = pd if pd in themes else default_theme
            elif pd_name.startswith('plugin_'):
                plugin_id = pd_name.replace('plugin_', '', 1)
                if not any(plugin.id == plugin_id for plugin in plugins):
                    continue
                post_disabled_plugins.append(plugin_id)
            else:
                resp.set_cookie(pd_name, pd, max_age=cookie_max_age)

        disabled_plugins = []
        allowed_plugins = []
        for plugin in plugins:
            if plugin.default_on:
                if plugin.id in post_disabled_plugins:
                    disabled_plugins.append(plugin.id)
            elif plugin.id not in post_disabled_plugins:
                allowed_plugins.append(plugin.id)

        resp.set_cookie('disabled_plugins', ','.join(disabled_plugins), max_age=cookie_max_age)

        resp.set_cookie('allowed_plugins', ','.join(allowed_plugins), max_age=cookie_max_age)

        resp.set_cookie(
            'blocked_engines', ','.join('__'.join(e) for e in blocked_engines),
            max_age=cookie_max_age
        )

        if locale:
            resp.set_cookie(
                'locale', locale,
                max_age=cookie_max_age
            )

        if lang:
            resp.set_cookie(
                'language', lang,
                max_age=cookie_max_age
            )

        if selected_categories:
            # cookie max age: 4 weeks
            resp.set_cookie(
                'categories', ','.join(selected_categories),
                max_age=cookie_max_age
            )

            resp.set_cookie(
                'autocomplete', autocomplete,
                max_age=cookie_max_age
            )

        resp.set_cookie('method', method, max_age=cookie_max_age)

        resp.set_cookie('safesearch', safesearch, max_age=cookie_max_age)

        resp.set_cookie('image_proxy', image_proxy, max_age=cookie_max_age)

        resp.set_cookie('theme', theme, max_age=cookie_max_age)

        return resp

    # stats for preferences page
    stats = {}

    for c in categories:
        for e in categories[c]:
            stats[e.name] = {'time': None,
                             'warn_timeout': False,
                             'warn_time': False}
            if e.timeout > settings['outgoing']['request_timeout']:
                stats[e.name]['warn_timeout'] = True

    for engine_stat in get_engines_stats()[0][1]:
        stats[engine_stat.get('name')]['time'] = round(engine_stat.get('avg'), 3)
        if engine_stat.get('avg') > settings['outgoing']['request_timeout']:
            stats[engine_stat.get('name')]['warn_time'] = True
    # end of stats

    return render('preferences.html',
                  locales=settings['locales'],
                  current_locale=get_locale(),
                  current_language=lang or 'all',
                  image_proxy=image_proxy,
                  language_codes=language_codes,
                  engines_by_category=categories,
                  stats=stats,
                  blocked_engines=blocked_engines,
                  autocomplete_backends=autocomplete_backends,
                  shortcuts={y: x for x, y in engine_shortcuts.items()},
                  themes=themes,
                  plugins=plugins,
                  allowed_plugins=[plugin.id for plugin in request.user_plugins],
                  theme=get_current_theme_name())


@app.route('/image_proxy', methods=['GET'])
def image_proxy():
    url = request.args.get('url').encode('utf-8')

    if not url:
        return '', 400

    h = hashlib.sha256(url + settings['server']['secret_key'].encode('utf-8')).hexdigest()

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

    img = ''
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
    stats = get_engines_stats()
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
""", mimetype='text/plain')


@app.route('/opensearch.xml', methods=['GET'])
def opensearch():
    method = 'post'

    if request.cookies.get('method', 'POST') == 'GET':
        method = 'get'

    # chrome/chromium only supports HTTP GET....
    if request.headers.get('User-Agent', '').lower().find('webkit') >= 0:
        method = 'get'

    ret = render('opensearch.xml',
                 opensearch_method=method,
                 host=get_base_url())

    resp = Response(response=ret,
                    status=200,
                    mimetype="text/xml")
    return resp


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path,
                                            'static/themes',
                                            get_current_theme_name(),
                                            'img'),
                               'favicon.png',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/clear_cookies')
def clear_cookies():
    resp = make_response(redirect(url_for('index')))
    for cookie_name in request.cookies:
        resp.delete_cookie(cookie_name)
    return resp


def run():
    app.run(
        debug=settings['general']['debug'],
        use_debugger=settings['general']['debug'],
        port=settings['server']['port'],
        host=settings['server']['bind_address']
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
