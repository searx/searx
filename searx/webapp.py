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

if __name__ == "__main__":
    from sys import path
    from os.path import realpath, dirname
    path.append(realpath(dirname(realpath(__file__))+'/../'))

from flask import Flask, request, render_template, url_for, Response, make_response, redirect, g
from searx.engines import search, categories
from searx import settings
import json
import sqlite3
from operator import itemgetter

app = Flask(__name__)
app.secret_key = settings.secret_key
app.database = settings.database

opensearch_xml = '''<?xml version="1.0" encoding="utf-8"?>
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
  <ShortName>searx</ShortName>
  <Description>Search searx</Description>
  <InputEncoding>UTF-8</InputEncoding>
  <LongName>searx meta search engine</LongName>
  <Url type="text/html" method="{method}" template="{host}">
    <Param name="q" value="{{searchTerms}}" />
  </Url>
</OpenSearchDescription>
'''

def render(template_name, **kwargs):
    global categories
    kwargs['categories'] = sorted(categories.keys())
    if not 'selected_categories' in kwargs:
        kwargs['selected_categories'] = []
        cookie_categories = request.cookies.get('categories', '').split(',')
        for ccateg in cookie_categories:
            if ccateg in categories:
                kwargs['selected_categories'].append(ccateg)
        if not len(kwargs['selected_categories']):
            kwargs['selected_categories'] = ['general']
    return render_template(template_name, **kwargs)

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.database)
    return db

def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    db.commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    global categories
    if request.method=='POST':
        request_data = request.form
    else:
        request_data = request.args
    if not request_data.get('q'):
        return render('index.html')
    selected_categories = []
    for pd_name,pd in request_data.items():
        if pd_name.startswith('category_'):
            category = pd_name[9:]
            if not category in categories:
                continue
            selected_categories.append(category)
    if not len(selected_categories):
        cookie_categories = request.cookies.get('categories', '').split(',')
        for ccateg in cookie_categories:
            if ccateg in categories:
                selected_categories.append(ccateg)

    query = request_data['q'].encode('utf-8')
    results = search(query, request, selected_categories)

    for result in results:
        if len(result['url']) > 74:
            result['pretty_url'] = result['url'][:35] + '[..]' + result['url'][-35:]
        else:
             result['pretty_url'] = result['url']

    if request_data.get('format') == 'json':
        return Response(json.dumps({'query': query, 'results': results}), mimetype='application/json')
    template = render('results.html'
                        ,results=results
                        ,q=query.decode('utf-8')
                        ,selected_categories=selected_categories
                        ,number_of_results=len(results)
                        )
    resp = make_response(template)
    resp.set_cookie('categories', ','.join(selected_categories))
    return resp

@app.route('/go', methods=['GET'])
def go():
    request_data = request.args

    # Let's find if the snippet exist or not, it's the combination of URL and content
    snippet = query_db('SELECT id FROM snippets WHERE url = ? and content = ? and title = ?', 
                        args=(request_data['url'], request_data['content'], request_data['title']), 
                        one=True)

    if snippet is None:
        # We do not have this snippet yet
        query_db('INSERT INTO snippets (url, content, title) VALUES(?, ?, ?)', args=(request_data['url'], request_data['content'], request_data['title']))
        snippet = query_db('SELECT id FROM snippets WHERE url = ? and content = ? and title = ?', 
                            args=(request_data['url'], request_data['content'], request_data['title']),
                            one=True)

    # Now we have snippet
    for term in request_data['q'].split():
        # Let's ignore too short terms
        if len(term) <= 3:
            continue
        # Let's see if the term exist
        current_term = query_db('SELECT id, score FROM results WHERE keyword = ? AND snippet = ?', args=(term, snippet[0]), one=True)
        if current_term is None:
            # First hit
            query_db('INSERT INTO results (keyword, snippet, score) VALUES (?, ?, 1)', args=(term, snippet[0]))
        else:
            # We need to increase the score
            query_db('UPDATE results SET score = ? WHERE id = ?', args=(current_term[1] + 1, current_term[0]))

    return redirect(request_data['url'])

@app.route('/lsearch', methods=['GET'])
def local_search():
    request_data = request.args
    arg_list = request_data['q'].split()
    query = 'SELECT snippet FROM results WHERE keyword in (%s)' % (', '.join(['?']*len(arg_list),))
    snippets = query_db(query, args=tuple(arg_list))
    results = []
    for snippet_id in snippets:
        snippet = query_db('SELECT content, title, url FROM snippets WHERE id = ?', args=(str(snippet_id[0]),), one=True)
        if snippet is not None:
            result = {'content': snippet[0], 'title': snippet[1], 'url': snippet[2]}
            results.append(result)

    return json.dumps(results)

@app.route('/favicon.ico', methods=['GET'])
def fav():
    return ''

@app.route('/about', methods=['GET'])
def about():
    global categories
    return render('about.html', categs=categories.items())

@app.route('/opensearch.xml', methods=['GET'])
def opensearch():
    global opensearch_xml
    method = 'post'
    # chrome/chromium only supports HTTP GET....
    if request.headers.get('User-Agent', '').lower().find('webkit') >= 0:
        method = 'get'
    ret = opensearch_xml.format(method=method, host=url_for('index', _external=True))
    resp = Response(response=ret,
                status=200,
                mimetype="application/xml")
    return resp

if __name__ == "__main__":
    from gevent import monkey
    monkey.patch_all()

    app.run(debug        = settings.debug
           ,use_debugger = settings.debug
           ,port         = settings.port
           ,threaded     = True
           )
