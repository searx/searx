
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

from os.path import realpath, dirname, splitext, join
from os import listdir
from imp import load_source
import grequests
from itertools import izip_longest, chain
from operator import itemgetter

engine_dir = dirname(realpath(__file__))

engines = {}

categories = {'general': []}

for filename in listdir(engine_dir):
    modname = splitext(filename)[0]
    if filename.startswith('_') or not filename.endswith('.py'):
        continue
    filepath = join(engine_dir, filename)
    engine = load_source(modname, filepath)
    engine.name = modname
    if not hasattr(engine, 'request') or not hasattr(engine, 'response'):
        continue
    engines[modname] = engine
    if not hasattr(engine, 'categories'):
        categories['general'].append(engine)
    else:
        for category_name in engine.categories:
            categories.setdefault(category_name, []).append(engine)

def default_request_params():
    return {'method': 'GET', 'headers': {}, 'data': {}, 'url': ''}

def make_callback(engine_name, results, callback):
    def process_callback(response, **kwargs):
        cb_res = []
        for result in callback(response):
            result['engine'] = engine_name
            cb_res.append(result)
        results[engine_name] = cb_res
    return process_callback

def search(query, request, selected_engines):
    global engines
    requests = []
    results = {}
    user_agent = request.headers.get('User-Agent', '')
    for ename, engine in engines.items():
        if ename not in selected_engines:
            continue
        headers = default_request_params()
        headers['User-Agent'] = user_agent
        request_params = engine.request(query, headers)
        callback = make_callback(ename, results, engine.response)
        if request_params['method'] == 'GET':
            req = grequests.get(request_params['url']
                                ,headers=headers
                                ,hooks=dict(response=callback)
                                )
        else:
            req = grequests.post(request_params['url']
                                ,data=request_params['data']
                                ,headers=headers
                                ,hooks=dict(response=callback)
                                )
        requests.append(req)
    grequests.map(requests)
    flat_res = list(filter(None, chain(*izip_longest(*results.values()))))
    flat_len = len(flat_res)
    results = []
    # deduplication + scoring
    for i,res in enumerate(flat_res):
        score = flat_len - i
        duplicated = False
        for new_res in results:
            if res['url'] == new_res['url']:
                duplicated = new_res
                break
        if duplicated:
            if len(res.get('content', '')) > len(duplicated.get('content', '')):
                duplicated['content'] = res['content']
            duplicated['score'] += score
        else:
            res['score'] = score
            results.append(res)

    return sorted(results, key=itemgetter('score'), reverse=True)
