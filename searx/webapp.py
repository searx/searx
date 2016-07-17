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
from urlparse import urlparse, urljoin
from werkzeug.contrib.fixers import ProxyFix
from flask import (
    Flask, request, render_template, url_for, Response, make_response,
    redirect, send_from_directory
)
from flask_babel import Babel, gettext, format_date, format_decimal
from flask.json import jsonify
from searx import settings, searx_dir
from searx.engines import (
    categories, engines, get_engines_stats, engine_shortcuts
)
from searx.utils import (
    UnicodeWriter, highlight_content, html_to_text, get_themes,
    get_static_files, get_result_templates, gen_useragent, dict_subset,
    prettify_url
)
from searx.version import VERSION_STRING
from searx.languages import language_codes
from searx.search import Search
from searx.query import Query
from searx.autocomplete import searx_bang, backends as autocomplete_backends
from searx.plugins import plugins
from searx.preferences import Preferences, ValidationException

# check if the pyopenssl, ndg-httpsclient, pyasn1 packages are installed.
# They are needed for SSL connection without trouble, see #298
try:
    import OpenSSL.SSL  # NOQA
    import ndg.httpsclient  # NOQA
    import pyasn1  # NOQA
except ImportError:
    logger.critical("The pyopenssl, ndg-httpsclient, pyasn1 packages have to be installed.\n"
                    "Some HTTPS connections will fail")


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

outgoing_proxies = settings['outgoing'].get('proxies', None)


@babel.localeselector
def get_locale():
    locale = request.accept_languages.best_match(settings['locales'].keys())

    if request.preferences.get_value('locale') != '':
        locale = request.preferences.get_value('locale')

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


def image_proxify(url):

    if url.startswith('//'):
        url = 'https:' + url

    if not request.preferences.get_value('image_proxy'):
        return url

    hash_string = url + settings['server']['secret_key']
    h = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

    return '{0}?{1}'.format(url_for('image_proxy'),
                            urlencode(dict(url=url.encode('utf-8'), h=h)))


def render(template_name, override_theme=None, **kwargs):
    disabled_engines = request.preferences.engines.get_disabled()

    enabled_categories = set(category for engine_name in engines
                             for category in engines[engine_name].categories
                             if (engine_name, category) not in disabled_engines)

    if 'categories' not in kwargs:
        kwargs['categories'] = ['general']
        kwargs['categories'].extend(x for x in
                                    sorted(categories.keys())
                                    if x != 'general'
                                    and x in enabled_categories)

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
        cookie_categories = request.preferences.get_value('categories')
        for ccateg in cookie_categories:
            kwargs['selected_categories'].append(ccateg)

    if not kwargs['selected_categories']:
        kwargs['selected_categories'] = ['general']

    if 'autocomplete' not in kwargs:
        kwargs['autocomplete'] = request.preferences.get_value('autocomplete')

    if get_locale() in rtl_locales and 'rtl' not in kwargs:
        kwargs['rtl'] = True

    kwargs['searx_version'] = VERSION_STRING

    kwargs['method'] = request.preferences.get_value('method')

    kwargs['safesearch'] = str(request.preferences.get_value('safesearch'))

    # override url_for function in templates
    kwargs['url_for'] = url_for_theme

    kwargs['image_proxify'] = image_proxify

    kwargs['get_result_template'] = get_result_template

    kwargs['theme'] = get_current_theme_name(override=override_theme)

    kwargs['template_name'] = template_name

    kwargs['cookies'] = request.cookies

    kwargs['instance_name'] = settings['general']['instance_name']

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
    preferences = Preferences(themes, categories.keys(), engines, plugins)
    preferences.parse_cookies(request.cookies)
    request.preferences = preferences

    request.form = dict(request.form.items())
    for k, v in request.args.items():
        if k not in request.form:
            request.form[k] = v

    request.user_plugins = []
    allowed_plugins = preferences.plugins.get_enabled()
    disabled_plugins = preferences.plugins.get_disabled()
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

    results = search.result_container.get_ordered_results()

    for result in results:

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

    number_of_results = search.result_container.results_number()
    if number_of_results < search.result_container.results_length():
        number_of_results = 0

    if search.request_data.get('format') == 'json':
        return Response(json.dumps({'query': search.query,
                                    'number_of_results': number_of_results,
                                    'results': results}),
                        mimetype='application/json')
    elif search.request_data.get('format') == 'csv':
        csv = UnicodeWriter(cStringIO.StringIO())
        keys = ('title', 'url', 'content', 'host', 'engine', 'score')
        csv.writerow(keys)
        for row in results:
            row['host'] = row['parsed_url'].netloc
            csv.writerow([row.get(key, '') for key in keys])
        csv.stream.seek(0)
        response = Response(csv.stream.read(), mimetype='application/csv')
        cont_disp = 'attachment;Filename=searx_-_{0}.csv'.format(search.query.encode('utf-8'))
        response.headers.add('Content-Disposition', cont_disp)
        return response
    elif search.request_data.get('format') == 'rss':
        response_rss = render(
            'opensearch_response_rss.xml',
            results=results,
            q=search.request_data['q'],
            number_of_results=number_of_results,
            base_url=get_base_url()
        )
        return Response(response_rss, mimetype='text/xml')

    return render(
        'results.html',
        results=results,
        q=search.request_data['q'],
        selected_categories=search.categories,
        paging=search.paging,
        number_of_results=format_decimal(number_of_results),
        pageno=search.pageno,
        time_range=search.time_range,
        base_url=get_base_url(),
        suggestions=search.result_container.suggestions,
        answers=search.result_container.answers,
        infoboxes=search.result_container.infoboxes,
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
    disabled_engines = request.preferences.engines.get_disabled()

    # parse query
    query = Query(request_data.get('q', '').encode('utf-8'), disabled_engines)
    query.parse_query()

    # check if search query is set
    if not query.getSearchQuery():
        return '', 400

    # run autocompleter
    completer = autocomplete_backends.get(request.preferences.get_value('autocomplete'))

    # parse searx specific autocompleter results like !bang
    raw_results = searx_bang(query)

    # normal autocompletion results only appear if max 3 inner results returned
    if len(raw_results) <= 3 and completer:
        # get language from cookie
        language = request.preferences.get_value('language')
        if not language or language == 'all':
            language = 'en'
        else:
            language = language.split('_')[0]
        # run autocompletion
        raw_results.extend(completer(query.getSearchQuery(), language))

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
    """Render preferences page && save user preferences"""

    # save preferences
    if request.method == 'POST':
        resp = make_response(redirect(urljoin(settings['server']['base_url'], url_for('index'))))
        try:
            request.preferences.parse_form(request.form)
        except ValidationException:
            # TODO use flash feature of flask
            return resp
        return request.preferences.save(resp)

    # render preferences
    image_proxy = request.preferences.get_value('image_proxy')
    lang = request.preferences.get_value('language')
    disabled_engines = request.preferences.engines.get_disabled()
    allowed_plugins = request.preferences.plugins.get_enabled()

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
                  current_language=lang,
                  image_proxy=image_proxy,
                  language_codes=language_codes,
                  engines_by_category=categories,
                  stats=stats,
                  disabled_engines=disabled_engines,
                  autocomplete_backends=autocomplete_backends,
                  shortcuts={y: x for x, y in engine_shortcuts.items()},
                  themes=themes,
                  plugins=plugins,
                  allowed_plugins=allowed_plugins,
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

    if request.preferences.get_value('method') == 'GET':
        method = 'get'

    # chrome/chromium only supports HTTP GET....
    if request.headers.get('User-Agent', '').lower().find('webkit') >= 0:
        method = 'get'

    ret = render('opensearch.xml',
                 opensearch_method=method,
                 host=get_base_url(),
                 urljoin=urljoin)

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
    resp = make_response(redirect(urljoin(settings['server']['base_url'], url_for('index'))))
    for cookie_name in request.cookies:
        resp.delete_cookie(cookie_name)
    return resp


@app.route('/config')
def config():
    return jsonify({'categories': categories.keys(),
                    'engines': [{'name': engine_name,
                                 'categories': engine.categories,
                                 'shortcut': engine.shortcut,
                                 'enabled': not engine.disabled}
                                for engine_name, engine in engines.items()],
                    'plugins': [{'name': plugin.name,
                                 'enabled': plugin.default_on}
                                for plugin in plugins],
                    'instance_name': settings['general']['instance_name'],
                    'locales': settings['locales'],
                    'default_locale': settings['ui']['default_locale'],
                    'autocomplete': settings['search']['autocomplete'],
                    'safe_search': settings['search']['safe_search'],
                    'default_theme': settings['ui']['default_theme']})


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
