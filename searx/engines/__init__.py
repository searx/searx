
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

import sys
import threading
from os.path import realpath, dirname
from flask_babel import gettext
from operator import itemgetter
from json import loads
from requests import get
from searx import settings
from searx import logger
from searx.utils import load_module


logger = logger.getChild('engines')

engine_dir = dirname(realpath(__file__))

engines = {}

categories = {'general': []}

languages = loads(open(engine_dir + '/../data/engines_languages.json').read())

engine_shortcuts = {}
engine_default_args = {'paging': False,
                       'categories': ['general'],
                       'language_support': True,
                       'supported_languages': [],
                       'safesearch': False,
                       'timeout': settings['outgoing']['request_timeout'],
                       'shortcut': '-',
                       'disabled': False,
                       'suspend_end_time': 0,
                       'continuous_errors': 0,
                       'time_range_support': False}


def load_engine(engine_data):

    if '_' in engine_data['name']:
        logger.error('Engine name conains underscore: "{}"'.format(engine_data['name']))
        sys.exit(1)

    engine_module = engine_data['engine']

    try:
        engine = load_module(engine_module + '.py', engine_dir)
    except:
        logger.exception('Cannot load engine "{}"'.format(engine_module))
        return None

    for param_name in engine_data:
        if param_name == 'engine':
            continue
        if param_name == 'categories':
            if engine_data['categories'] == 'none':
                engine.categories = []
            else:
                engine.categories = list(map(str.strip, engine_data['categories'].split(',')))
            continue
        setattr(engine, param_name, engine_data[param_name])

    for arg_name, arg_value in engine_default_args.items():
        if not hasattr(engine, arg_name):
            setattr(engine, arg_name, arg_value)

    # checking required variables
    for engine_attr in dir(engine):
        if engine_attr.startswith('_'):
            continue
        if engine_attr == 'inactive' and getattr(engine, engine_attr) is True:
            return None
        if getattr(engine, engine_attr) is None:
            logger.error('Missing engine config attribute: "{0}.{1}"'
                         .format(engine.name, engine_attr))
            sys.exit(1)

    # assign supported languages from json file
    if engine_data['name'] in languages:
        setattr(engine, 'supported_languages', languages[engine_data['name']])

    # assign language fetching method if auxiliary method exists
    if hasattr(engine, '_fetch_supported_languages'):
        setattr(engine, 'fetch_supported_languages',
                lambda: engine._fetch_supported_languages(get(engine.supported_languages_url)))

    engine.stats = {
        'result_count': 0,
        'search_count': 0,
        'page_load_time': 0,
        'page_load_count': 0,
        'engine_time': 0,
        'engine_time_count': 0,
        'score_count': 0,
        'errors': 0
    }

    for category_name in engine.categories:
        categories.setdefault(category_name, []).append(engine)

    if engine.shortcut in engine_shortcuts:
        logger.error('Engine config error: ambigious shortcut: {0}'.format(engine.shortcut))
        sys.exit(1)

    engine_shortcuts[engine.shortcut] = engine.name

    return engine


def to_percentage(stats, maxvalue):
    for engine_stat in stats:
        if maxvalue:
            engine_stat['percentage'] = int(engine_stat['avg'] / maxvalue * 100)
        else:
            engine_stat['percentage'] = 0
    return stats


def get_engines_stats():
    # TODO refactor
    pageloads = []
    engine_times = []
    results = []
    scores = []
    errors = []
    scores_per_result = []

    max_pageload = max_engine_times = max_results = max_score = max_errors = max_score_per_result = 0  # noqa
    for engine in engines.values():
        if engine.stats['search_count'] == 0:
            continue
        results_num = \
            engine.stats['result_count'] / float(engine.stats['search_count'])

        if engine.stats['page_load_count'] != 0:
            load_times = engine.stats['page_load_time'] / float(engine.stats['page_load_count'])  # noqa
        else:
            load_times = 0

        if engine.stats['engine_time_count'] != 0:
            this_engine_time = engine.stats['engine_time'] / float(engine.stats['engine_time_count'])  # noqa
        else:
            this_engine_time = 0

        if results_num:
            score = engine.stats['score_count'] / float(engine.stats['search_count'])  # noqa
            score_per_result = score / results_num
        else:
            score = score_per_result = 0.0

        max_pageload = max(load_times, max_pageload)
        max_engine_times = max(this_engine_time, max_engine_times)
        max_results = max(results_num, max_results)
        max_score = max(score, max_score)
        max_score_per_result = max(score_per_result, max_score_per_result)
        max_errors = max(max_errors, engine.stats['errors'])

        pageloads.append({'avg': load_times, 'name': engine.name})
        engine_times.append({'avg': this_engine_time, 'name': engine.name})
        results.append({'avg': results_num, 'name': engine.name})
        scores.append({'avg': score, 'name': engine.name})
        errors.append({'avg': engine.stats['errors'], 'name': engine.name})
        scores_per_result.append({
            'avg': score_per_result,
            'name': engine.name
        })

    pageloads = to_percentage(pageloads, max_pageload)
    engine_times = to_percentage(engine_times, max_engine_times)
    results = to_percentage(results, max_results)
    scores = to_percentage(scores, max_score)
    scores_per_result = to_percentage(scores_per_result, max_score_per_result)
    erros = to_percentage(errors, max_errors)

    return [
        (
            gettext('Engine time (sec)'),
            sorted(engine_times, key=itemgetter('avg'))
        ),
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


def load_engines(engine_list):
    global engines
    engines.clear()
    for engine_data in engine_list:
        engine = load_engine(engine_data)
        if engine is not None:
            engines[engine.name] = engine
    return engines


def initialize_engines(engine_list):
    load_engines(engine_list)
    for engine in engines.items():
        if hasattr(engine, 'init'):
            init_fn = getattr(engine, engine_attr)

            def engine_init():
                init_fn()
                logger.debug('%s engine initialized', engine_data['name'])
            logger.debug('Starting background initialization of %s engine', engine_data['name'])
            threading.Thread(target=engine_init).start()
