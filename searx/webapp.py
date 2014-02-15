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
    path.append(realpath(dirname(realpath(__file__))+'/../'))

import json
import cStringIO
import os

from flask import (
    Flask, request, render_template, url_for, Response, make_response,
    redirect, send_from_directory
)
from flask.ext.babel import Babel
from searx import settings, searx_dir
from searx.engines import (
    search as do_search, categories, engines, get_engines_stats,
    engine_shortcuts
)
from searx.utils import UnicodeWriter, highlight_content, html_to_text
from searx.languages import language_codes
from searx.search import Search


app = Flask(
    __name__,
    static_folder=os.path.join(searx_dir, 'static'),
    template_folder=os.path.join(searx_dir, 'templates')
)

app.secret_key = settings['server']['secret_key']

babel = Babel(app)

#TODO configurable via settings.yml
favicons = ['wikipedia', 'youtube', 'vimeo', 'soundcloud',
            'twitter', 'stackoverflow', 'github']


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


def render(template_name, **kwargs):
    global categories
    kwargs['categories'] = ['general']
    kwargs['categories'].extend(x for x in
                                sorted(categories.keys()) if x != 'general')
    if not 'selected_categories' in kwargs:
        kwargs['selected_categories'] = []
        cookie_categories = request.cookies.get('categories', '').split(',')
        for ccateg in cookie_categories:
            if ccateg in categories:
                kwargs['selected_categories'].append(ccateg)
        if not kwargs['selected_categories']:
            kwargs['selected_categories'] = ['general']
    return render_template(template_name, **kwargs)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Render index page.

    Supported outputs: html, json, csv, rss.
    """

    if not request.args and not request.form:
        return render('index.html')

    try:
        search = Search(request)
    except:
        return render('index.html')

    # TODO moar refactor - do_search integration into Search class
    search.results, search.suggestions = do_search(search.query,
                                                   request,
                                                   search.engines,
                                                   search.pageno,
                                                   search.lang)

    for result in search.results:
        if not search.paging and engines[result['engine']].paging:
            search.paging = True
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
        suggestions=search.suggestions
    )


@app.route('/about', methods=['GET'])
def about():
    """Render about page"""
    return render('about.html')


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
    else:
        selected_categories = []
        locale = None
        for pd_name, pd in request.form.items():
            if pd_name.startswith('category_'):
                category = pd_name[9:]
                if not category in categories:
                    continue
                selected_categories.append(category)
            elif pd_name == 'locale' and pd in settings['locales']:
                locale = pd
            elif pd_name == 'language' and (pd == 'all' or
                                            pd in (x[0] for
                                                   x in language_codes)):
                lang = pd
            elif pd_name.startswith('engine_'):
                engine_name = pd_name.replace('engine_', '', 1)
                if engine_name in engines:
                    blocked_engines.append(engine_name)

        resp = make_response(redirect('/'))

        user_blocked_engines = request.cookies.get('blocked_engines', '').split(',')  # noqa

        if sorted(blocked_engines) != sorted(user_blocked_engines):
            # cookie max age: 4 weeks
            resp.set_cookie(
                'blocked_engines', ','.join(blocked_engines),
                max_age=60 * 60 * 24 * 7 * 4
            )

        if locale:
            # cookie max age: 4 weeks
            resp.set_cookie(
                'locale', locale,
                max_age=60 * 60 * 24 * 7 * 4
            )

        if lang:
            # cookie max age: 4 weeks
            resp.set_cookie(
                'language', lang,
                max_age=60 * 60 * 24 * 7 * 4
            )

        if selected_categories:
            # cookie max age: 4 weeks
            resp.set_cookie(
                'categories', ','.join(selected_categories),
                max_age=60 * 60 * 24 * 7 * 4
            )
        return resp
    return render('preferences.html',
                  locales=settings['locales'],
                  current_locale=get_locale(),
                  current_language=lang or 'all',
                  language_codes=language_codes,
                  categs=categories.items(),
                  blocked_engines=blocked_engines,
                  shortcuts={y: x for x, y in engine_shortcuts.items()})


@app.route('/stats', methods=['GET'])
def stats():
    """Render engine statistics page."""
    global categories
    stats = get_engines_stats()
    return render('stats.html', stats=stats)


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
    ret = render('opensearch.xml', method=method, host=get_base_url())
    resp = Response(response=ret,
                    status=200,
                    mimetype="application/xml")
    return resp


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img'),
                               'favicon.png',
                               mimetype='image/vnd.microsoft.icon')


def run():
    from gevent import monkey
    monkey.patch_all()

    app.run(
        debug=settings['server']['debug'],
        use_debugger=settings['server']['debug'],
        port=settings['server']['port']
    )


if __name__ == "__main__":
    run()
