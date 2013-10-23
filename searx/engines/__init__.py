
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
from imp import load_source
import grequests
from itertools import izip_longest, chain
from operator import itemgetter
from urlparse import urlparse
from searx import settings
import ConfigParser
import sys

engine_dir = dirname(realpath(__file__))
searx_dir  = join(engine_dir, '../../')

engines_config = ConfigParser.SafeConfigParser()
engines_config.read(join(searx_dir, 'engines.cfg'))

engines = {}

categories = {'general': []}

def load_module(filename):
    modname = splitext(filename)[0]
    if modname in sys.modules:
        del sys.modules[modname]
    filepath = join(engine_dir, filename)
    module = load_source(modname, filepath)
    module.name = modname
    return module

for section in engines_config.sections():
    engine_data = engines_config.options(section)
    engine = load_module(engines_config.get(section, 'engine')+'.py')
    engine.name = section
    for param_name in engine_data:
        if param_name == 'engine':
            continue
        if param_name == 'categories':
            engine.categories = map(str.strip, engines_config.get(section, param_name).split(','))
            continue
        setattr(engine, param_name, engines_config.get(section, param_name))
    engines[engine.name] = engine
    if hasattr(engine, 'categories'):
        for category_name in engine.categories:
            categories.setdefault(category_name, []).append(engine)
    else:
        categories['general'].append(engine)

def default_request_params():
    return {'method': 'GET', 'headers': {}, 'data': {}, 'url': '', 'cookies': {}}

def make_callback(engine_name, results, callback):
    def process_callback(response, **kwargs):
        cb_res = []
        for result in callback(response):
            result['engine'] = engine_name
            cb_res.append(result)
        results[engine_name] = cb_res
    return process_callback

def search(query, request, selected_categories):
    global engines, categories
    requests = []
    results = {}
    selected_engines = []
    user_agent = request.headers.get('User-Agent', '')
    if not len(selected_categories):
        selected_categories = ['general']
    for categ in selected_categories:
        selected_engines.extend({'category': categ, 'name': x.name} for x in categories[categ])
    for selected_engine in selected_engines:
        if selected_engine['name'] not in engines:
            continue
        engine = engines[selected_engine['name']]
        request_params = default_request_params()
        request_params['headers']['User-Agent'] = user_agent
        request_params['category'] = selected_engine['category']
        request_params = engine.request(query, request_params)
        callback = make_callback(selected_engine['name'], results, engine.response)
        if request_params['method'] == 'GET':
            req = grequests.get(request_params['url']
                                ,headers=request_params['headers']
                                ,hooks=dict(response=callback)
                                ,cookies = request_params['cookies']
                                )
        else:
            req = grequests.post(request_params['url']
                                ,data=request_params['data']
                                ,headers=request_params['headers']
                                ,hooks=dict(response=callback)
                                ,cookies = request_params['cookies']
                                )
        requests.append(req)
    grequests.map(requests)
    flat_res = filter(None, chain.from_iterable(izip_longest(*results.values())))
    flat_len = len(flat_res)
    results = []
    # deduplication + scoring
    for i,res in enumerate(flat_res):
        res['parsed_url'] = urlparse(res['url'])
        score = (flat_len - i)*settings.weights.get(res['engine'], 1)
        duplicated = False
        for new_res in results:
            if res['parsed_url'].netloc == new_res['parsed_url'].netloc and\
               res['parsed_url'].path == new_res['parsed_url'].path and\
               res['parsed_url'].query == new_res['parsed_url'].query and\
               res.get('template') == new_res.get('template'):
                duplicated = new_res
                break
        if duplicated:
            if len(res.get('content', '')) > len(duplicated.get('content', '')):
                duplicated['content'] = res['content']
            duplicated['score'] += score
            duplicated['engine'] += ', '+res['engine']
            if duplicated['parsed_url'].scheme == 'https':
                continue
            elif res['parsed_url'].scheme == 'https':
                duplicated['parsed_url'].scheme == 'https'
                duplicated['url'] = duplicated['parsed_url'].geturl()
        else:
            res['score'] = score
            results.append(res)

    return sorted(results, key=itemgetter('score'), reverse=True)
