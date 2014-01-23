
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
from searx.utils import gen_useragent
import sys
from datetime import datetime
from flask.ext.babel import gettext

engine_dir = dirname(realpath(__file__))

number_of_searches = 0

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

if not 'engines' in settings or not settings['engines']:
    print '[E] Error no engines found. Edit your settings.yml'
    exit(2)

for engine_data in settings['engines']:
    engine_name = engine_data['engine']
    engine = load_module(engine_name + '.py')
    for param_name in engine_data:
        if param_name == 'engine':
            continue
        if param_name == 'categories':
            if engine_data['categories'] == 'none':
                engine.categories = []
            else:
                engine.categories = map(
                    str.strip, engine_data['categories'].split(','))
            continue
        setattr(engine, param_name, engine_data[param_name])
    for engine_attr in dir(engine):
        if engine_attr.startswith('_'):
            continue
        if getattr(engine, engine_attr) is None:
            print '[E] Engine config error: Missing attribute "{0}.{1}"'.format(engine.name, engine_attr)  # noqa
            sys.exit(1)
    engines[engine.name] = engine
    engine.stats = {
        'result_count': 0,
        'search_count': 0,
        'page_load_time': 0,
        'score_count': 0,
        'errors': 0
    }
    if hasattr(engine, 'categories'):
        for category_name in engine.categories:
            categories.setdefault(category_name, []).append(engine)
    else:
        categories['general'].append(engine)


def default_request_params():
    return {
        'method': 'GET', 'headers': {}, 'data': {}, 'url': '', 'cookies': {}}


def make_callback(engine_name, results, suggestions, callback, params):
    # creating a callback wrapper for the search engine results
    def process_callback(response, **kwargs):
        cb_res = []
        response.search_params = params
        engines[engine_name].stats['page_load_time'] += \
            (datetime.now() - params['started']).total_seconds()
        try:
            search_results = callback(response)
        except Exception, e:
            engines[engine_name].stats['errors'] += 1
            results[engine_name] = cb_res
            print '[E] Error with engine "{0}":\n\t{1}'.format(
                engine_name, str(e))
            return
        for result in search_results:
            result['engine'] = engine_name
            if 'suggestion' in result:
                # TODO type checks
                suggestions.add(result['suggestion'])
                continue
            cb_res.append(result)
        results[engine_name] = cb_res
    return process_callback


def score_results(results):
    flat_res = filter(
        None, chain.from_iterable(izip_longest(*results.values())))
    flat_len = len(flat_res)
    engines_len = len(results)
    results = []
    # deduplication + scoring
    for i, res in enumerate(flat_res):
        res['parsed_url'] = urlparse(res['url'])
        res['engines'] = [res['engine']]
        weight = 1.0
        if hasattr(engines[res['engine']], 'weight'):
            weight = float(engines[res['engine']].weight)
        score = int((flat_len - i) / engines_len) * weight + 1
        duplicated = False
        for new_res in results:
            p1 = res['parsed_url'].path[:-1] if res['parsed_url'].path.endswith('/') else res['parsed_url'].path  # noqa
            p2 = new_res['parsed_url'].path[:-1] if new_res['parsed_url'].path.endswith('/') else new_res['parsed_url'].path  # noqa
            if res['parsed_url'].netloc == new_res['parsed_url'].netloc and\
               p1 == p2 and\
               res['parsed_url'].query == new_res['parsed_url'].query and\
               res.get('template') == new_res.get('template'):
                duplicated = new_res
                break
        if duplicated:
            if len(res.get('content', '')) > len(duplicated.get('content', '')):  # noqa
                duplicated['content'] = res['content']
            duplicated['score'] += score
            duplicated['engines'].append(res['engine'])
            if duplicated['parsed_url'].scheme == 'https':
                continue
            elif res['parsed_url'].scheme == 'https':
                duplicated['url'] = res['parsed_url'].geturl()
                duplicated['parsed_url'] = res['parsed_url']
        else:
            res['score'] = score
            results.append(res)
    return sorted(results, key=itemgetter('score'), reverse=True)


def search(query, request, selected_engines):
    global engines, categories, number_of_searches
    requests = []
    results = {}
    suggestions = set()
    number_of_searches += 1
    #user_agent = request.headers.get('User-Agent', '')
    user_agent = gen_useragent()

    for selected_engine in selected_engines:
        if selected_engine['name'] not in engines:
            continue

        engine = engines[selected_engine['name']]

        request_params = default_request_params()
        request_params['headers']['User-Agent'] = user_agent
        request_params['category'] = selected_engine['category']
        request_params['started'] = datetime.now()
        request_params = engine.request(query, request_params)

        callback = make_callback(
            selected_engine['name'],
            results,
            suggestions,
            engine.response,
            request_params
        )

        request_args = dict(
            headers=request_params['headers'],
            hooks=dict(response=callback),
            cookies=request_params['cookies'],
            timeout=settings['server']['request_timeout']
        )

        if request_params['method'] == 'GET':
            req = grequests.get
        else:
            req = grequests.post
            request_args['data'] = request_params['data']

        # ignoring empty urls
        if not request_params['url']:
            continue

        requests.append(req(request_params['url'], **request_args))
    grequests.map(requests)
    for engine_name, engine_results in results.items():
        engines[engine_name].stats['search_count'] += 1
        engines[engine_name].stats['result_count'] += len(engine_results)

    results = score_results(results)

    for result in results:
        for res_engine in result['engines']:
            engines[result['engine']].stats['score_count'] += result['score']

    return results, suggestions


def get_engines_stats():
    # TODO refactor
    pageloads = []
    results = []
    scores = []
    errors = []
    scores_per_result = []

    max_pageload = max_results = max_score = max_errors = max_score_per_result = 0  # noqa
    for engine in engines.values():
        if engine.stats['search_count'] == 0:
            continue
        results_num = \
            engine.stats['result_count'] / float(engine.stats['search_count'])
        load_times = engine.stats['page_load_time'] / float(engine.stats['search_count'])  # noqa
        if results_num:
            score = engine.stats['score_count'] / float(engine.stats['search_count'])  # noqa
            score_per_result = score / results_num
        else:
            score = score_per_result = 0.0
        max_results = max(results_num, max_results)
        max_pageload = max(load_times, max_pageload)
        max_score = max(score, max_score)
        max_score_per_result = max(score_per_result, max_score_per_result)
        max_errors = max(max_errors, engine.stats['errors'])
        pageloads.append({'avg': load_times, 'name': engine.name})
        results.append({'avg': results_num, 'name': engine.name})
        scores.append({'avg': score, 'name': engine.name})
        errors.append({'avg': engine.stats['errors'], 'name': engine.name})
        scores_per_result.append({
            'avg': score_per_result,
            'name': engine.name
        })

    for engine in pageloads:
        engine['percentage'] = int(engine['avg'] / max_pageload * 100)

    for engine in results:
        engine['percentage'] = int(engine['avg'] / max_results * 100)

    for engine in scores:
        engine['percentage'] = int(engine['avg'] / max_score * 100)

    for engine in scores_per_result:
        engine['percentage'] = int(engine['avg'] / max_score_per_result * 100)

    for engine in errors:
        if max_errors:
            engine['percentage'] = int(float(engine['avg']) / max_errors * 100)
        else:
            engine['percentage'] = 0

    return [
        (
            gettext('Page loads (sec)'),
            sorted(pageloads, key=itemgetter('avg'))
        ),
        (
            gettext('Number of results'),
            sorted(results, key=itemgetter('avg'), reverse=True)
        ),
        (
            gettext('Scores'),
            sorted(scores, key=itemgetter('avg'), reverse=True)
        ),
        (
            gettext('Scores per result'),
            sorted(scores_per_result, key=itemgetter('avg'), reverse=True)
        ),
        (
            gettext('Errors'),
            sorted(errors, key=itemgetter('avg'), reverse=True)
        ),
    ]
