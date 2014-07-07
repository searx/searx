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

from gevent import monkey
monkey.patch_all()


if __name__ == '__main__':
    from sys import path
    from os.path import realpath, dirname
    path.append(realpath(dirname(realpath(__file__))+'/../'))

import json
import cStringIO
import os

from datetime import datetime, timedelta
from itertools import chain
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
    UnicodeWriter, highlight_content, html_to_text, get_themes
)
from searx.https_rewrite import https_rules
from searx.languages import language_codes
from searx.search import Search
from searx.autocomplete import backends as autocomplete_backends


static_path, templates_path, themes =\
    get_themes(settings['themes_path']
               if settings.get('themes_path')
               else searx_dir)
default_theme = settings['default_theme'] if \
    settings.get('default_theme', None) else 'default'

app = Flask(
    __name__,
    static_folder=static_path,
    template_folder=templates_path
)

app.secret_key = settings['server']['secret_key']

babel = Babel(app)

#TODO configurable via settings.yml
favicons = ['wikipedia', 'youtube', 'vimeo', 'soundcloud',
            'twitter', 'stackoverflow', 'github']

cookie_max_age = 60 * 60 * 24 * 365 * 23  # 23 years


@babel.localeselector
def get_locale():
    locale = request.accept_languages.best_match(settings['locales'].keys())

    if request.cookies.get('locale', '') in settings['locales']:
        locale = request.cookies.get('locale', '')

    if 'locale' in request.args\
       and request.args['locale'] in settings['locales']:
        locale = request.args['locale']

    if 'locale' in request.form\
       and request.form['locale'] in settings['locales']:
        locale = request.form['locale']

    return locale


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
    theme_name = request.cookies.get('theme', default_theme)
    if theme_name not in themes:
        theme_name = default_theme
    return theme_name


def url_for_theme(endpoint, override_theme=None, **values):
    if endpoint == 'static' and values.get('filename', None):
        theme_name = get_current_theme_name(override=override_theme)
        values['filename'] = "{}/{}".format(theme_name, values['filename'])
    return url_for(endpoint, **values)


def render(template_name, override_theme=None, **kwargs):
    blocked_engines = request.cookies.get('blocked_engines', '').split(',')

    autocomplete = request.cookies.get('autocomplete')

    if autocomplete not in autocomplete_backends:
        autocomplete = None

    nonblocked_categories = (engines[e].categories
                             for e in engines
                             if e not in blocked_engines)

    nonblocked_categories = set(chain.from_iterable(nonblocked_categories))

    if not 'categories' in kwargs:
        kwargs['categories'] = ['general']
        kwargs['categories'].extend(x for x in
                                    sorted(categories.keys())
                                    if x != 'general'
                                    and x in nonblocked_categories)

    if not 'selected_categories' in kwargs:
        kwargs['selected_categories'] = []
        cookie_categories = request.cookies.get('categories', '').split(',')
        for ccateg in cookie_categories:
            if ccateg in categories:
                kwargs['selected_categories'].append(ccateg)
        if not kwargs['selected_categories']:
            kwargs['selected_categories'] = ['general']

    if not 'autocomplete' in kwargs:
        kwargs['autocomplete'] = autocomplete

    kwargs['method'] = request.cookies.get('method', 'POST')

    # override url_for function in templates
    kwargs['url_for'] = url_for_theme

    kwargs['theme'] = get_current_theme_name(override=override_theme)

    return render_template(
        '{}/{}'.format(kwargs['theme'], template_name), **kwargs)


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

    search.results, search.suggestions = search.search(request)

    for result in search.results:

        if not search.paging and engines[result['engine']].paging:
            search.paging = True

        if settings['server']['https_rewrite']\
           and result['parsed_url'].scheme == 'http':

            for http_regex, https_url in https_rules:
                if http_regex.match(result['url']):
                    result['url'] = http_regex.sub(https_url, result['url'])
                    # TODO result['parsed_url'].scheme
                    break

        # HTTPS rewrite
        if search.request_data.get('format', 'html') == 'html':
            if 'content' in result:
                result['content'] = highlight_content(result['content'],
                                                      search.query.encode('utf-8'))  # noqa
            result['title'] = highlight_content(result['title'],
                                                search.query.encode('utf-8'))
        else:
            if 'content' in result:
                result['content'] = html_to_text(result['content']).strip()
            # removing html content and whitespace duplications
            result['title'] = ' '.join(html_to_text(result['title'])
                                       .strip().split())

        if len(result['url']) > 74:
            url_parts = result['url'][:35], result['url'][-35:]
            result['pretty_url'] = u'{0}[...]{1}'.format(*url_parts)
        else:
            result['pretty_url'] = result['url']

        for engine in result['engines']:
            if engine in favicons:
                result['favicon'] = engine

        # TODO, check if timezone is calculated right
        if 'publishedDate' in result:
            if result['publishedDate'].replace(tzinfo=None)\
               >= datetime.now() - timedelta(days=1):
                timedifference = datetime.now() - result['publishedDate']\
                    .replace(tzinfo=None)
                minutes = int((timedifference.seconds / 60) % 60)
                hours = int(timedifference.seconds / 60 / 60)
                if hours == 0:
                    result['publishedDate'] = gettext(u'{minutes} minute(s) ago').format(minutes=minutes)  # noqa
                else:
                    result['publishedDate'] = gettext(u'{hours} hour(s), {minutes} minute(s) ago').format(hours=hours, minutes=minutes)  # noqa
            else:
                result['pubdate'] = result['publishedDate']\
                    .strftime('%a, %d %b %Y %H:%M:%S %z')
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
        theme=get_current_theme_name()
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

    if request.method == 'POST':
        request_data = request.form
    else:
        request_data = request.args

    # TODO fix XSS-vulnerability
    query = request_data.get('q', '').encode('utf-8')

    if not query:
        return

    completer = autocomplete_backends.get(request.cookies.get('autocomplete'))

    if not completer:
        return

    results = completer(query)

    if request_data.get('format') == 'x-suggestions':
        return Response(json.dumps([query, results]),
                        mimetype='application/json')
    else:
        return Response(json.dumps(results),
                        mimetype='application/json')


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    """Render preferences page.

    Settings that are going to be saved as cookies."""
    lang = None

    if request.cookies.get('language')\
       and request.cookies['language'] in (x[0] for x in language_codes):
        lang = request.cookies['language']

    blocked_engines = []

    if request.method == 'GET':
        blocked_engines = request.cookies.get('blocked_engines', '').split(',')
    else:  # on save
        selected_categories = []
        locale = None
        autocomplete = ''
        method = 'POST'
        for pd_name, pd in request.form.items():
            if pd_name.startswith('category_'):
                category = pd_name[9:]
                if not category in categories:
                    continue
                selected_categories.append(category)
            elif pd_name == 'locale' and pd in settings['locales']:
                locale = pd
            elif pd_name == 'autocomplete':
                autocomplete = pd
            elif pd_name == 'language' and (pd == 'all' or
                                            pd in (x[0] for
                                                   x in language_codes)):
                lang = pd
            elif pd_name == 'method':
                method = pd
            elif pd_name.startswith('engine_'):
                engine_name = pd_name.replace('engine_', '', 1)
                if engine_name in engines:
                    blocked_engines.append(engine_name)
            elif pd_name == 'theme':
                theme = pd if pd in themes else default_theme

        resp = make_response(redirect(url_for('index')))

        user_blocked_engines = request.cookies.get('blocked_engines', '').split(',')  # noqa

        if sorted(blocked_engines) != sorted(user_blocked_engines):
            resp.set_cookie(
                'blocked_engines', ','.join(blocked_engines),
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

        resp.set_cookie(
            'theme', theme, max_age=cookie_max_age)

        return resp
    return render('preferences.html',
                  locales=settings['locales'],
                  current_locale=get_locale(),
                  current_language=lang or 'all',
                  language_codes=language_codes,
                  categs=categories.items(),
                  blocked_engines=blocked_engines,
                  autocomplete_backends=autocomplete_backends,
                  shortcuts={y: x for x, y in engine_shortcuts.items()},
                  themes=themes,
                  theme=get_current_theme_name())


@app.route('/stats', methods=['GET'])
def stats():
    """Render engine statistics page."""
    global categories
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
    # chrome/chromium only supports HTTP GET....
    if request.headers.get('User-Agent', '').lower().find('webkit') >= 0:
        method = 'get'

    ret = render('opensearch.xml',
                 opensearch_method=method,
                 host=get_base_url())

    resp = Response(response=ret,
                    status=200,
                    mimetype="application/xml")
    return resp


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path,
                                            'static',
                                            get_current_theme_name(),
                                            'img'),
                               'favicon.png',
                               mimetype='image/vnd.microsoft.icon')


def run():
    app.run(
        debug=settings['server']['debug'],
        use_debugger=settings['server']['debug'],
        port=settings['server']['port']
    )


application = app


if __name__ == "__main__":
    run()
