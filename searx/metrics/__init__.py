# SPDX-License-Identifier: AGPL-3.0-or-later

import typing
import contextlib
from time import perf_counter
from operator import itemgetter

from flask_babel import gettext

from searx.engines import engines
from .models import MeasureStorage, CounterStorage
from .error_recorder import record_error, record_exception, errors_per_engines

__all__ = ["initialize",
           "get_engines_stats", "get_engine_errors",
           "measure", "record_duration",
           "counter", "counter_inc", "counter_add",
           "record_error", "record_exception"]


measure_storage: typing.Optional[MeasureStorage] = None
counter_storage: typing.Optional[CounterStorage] = None


@contextlib.contextmanager
def record_duration(*args):
    before = perf_counter()
    yield
    duration = perf_counter() - before
    measure = measure_storage.get(*args)
    if measure:
        measure.record(duration)
    else:
        raise ValueError("measure " + repr((*args,)) + " doesn't not exist")


def add_measure(duration, *args):
    measure_storage.get(*args).record(duration)


def counter_inc(*args):
    counter_storage.add(1, *args)


def counter_add(value, *args):
    counter_storage.add(value, *args)


def measure(*args):
    return measure_storage.get(*args)


def counter(*args):
    return counter_storage.get(*args)


def initialize(engine_names=None):
    global measure_storage, counter_storage

    measure_storage = MeasureStorage()
    counter_storage = CounterStorage()

    time_max = 60
    time_width = 0.1

    # initialize metrics
    # response time of a search (everything)
    measure_storage.configure(time_width, time_max, 'webapp', 'time')
    # response time of a search, without rendering
    measure_storage.configure(time_width, time_max, 'webapp', 'time', 'search')
    # response time of a search, only rendering
    measure_storage.configure(time_width, time_max, 'webapp', 'time', 'render')
    for engine_name in engine_names or engines:
        # search count
        counter_storage.configure(engine_name, 'search', 'count', 'sent')
        counter_storage.configure(engine_name, 'search', 'count', 'successful')
        # global counter of errors
        counter_storage.configure(engine_name, 'search', 'count', 'error')
        # result count per requests
        measure_storage.configure(1, 100, engine_name, 'result', 'count')
        # time doing HTTP requests
        measure_storage.configure(time_width, time_max, engine_name, 'time', 'http')
        # time for calling the "request" function
        measure_storage.configure(time_width, time_max, engine_name, 'time', 'request')
        # time for calling the "response" function
        measure_storage.configure(time_width, time_max, engine_name, 'time', 'response')
        # global time (request, search, callback, append)
        # call everytime, even if the callback hasn't really call
        # to keep the call count synchronize with <engine>, time, search
        measure_storage.configure(time_width, time_max, engine_name, 'time', 'total')
        # score of the engine
        counter_storage.configure(engine_name, 'score')


def get_engine_errors():
    global errors_per_engines

    result = {}
    engine_names = list(errors_per_engines.keys())
    engine_names.sort()
    for engine_name in engine_names:
        error_stats = errors_per_engines[engine_name]
        sent_search_count = max(counter(engine_name, 'search', 'count', 'sent'), 1)
        sorted_context_count_list = sorted(error_stats.items(), key=lambda context_count: context_count[1])
        r = []
        percentage_sum = 0
        for context, count in sorted_context_count_list:
            percentage = round(20 * count / sent_search_count) * 5
            percentage_sum += percentage
            r.append({
                'filename': context.filename,
                'function': context.function,
                'line_no': context.line_no,
                'code': context.code,
                'exception_classname': context.exception_classname,
                'log_message': context.log_message,
                'log_parameters': context.log_parameters,
                'percentage': percentage,
            })
        result[engine_name] = sorted(r, reverse=True, key=lambda d: d['percentage'])
    return result


def get_engines_stats(engine_list):
    global counter_storage, measure_storage

    assert counter_storage is not None
    assert measure_storage is not None

    stats = []
    max_error = max_score_per_result = 0  # noqa

    for engine in engine_list.values():
        engine_name = engine.name

        m_result_count = measure_storage.get(engine.name, 'result', 'count')
        score_count = counter_storage.get(engine.name, 'score')

        result_count_avg = m_result_count.average
        search_count = counter_storage.get(engine.name, 'search', 'count', 'successful')
        if search_count == 0:
            continue

        if result_count_avg > 0:
            score = score_count / float(search_count)  # noqa
            score_per_result = score / result_count_avg
        else:
            score = score_per_result = 0.0

        stat = {
            'name': engine_name,
            'time_request': measure_storage.get(engine_name, 'time', 'request').average,  # noqa
            'time_http': measure_storage.get(engine_name, 'time', 'http').average,  # noqa
            'time_response': measure_storage.get(engine_name, 'time', 'response').average,  # noqa
            'time_total': measure_storage.get(engine_name, 'time', 'total').average,  # noqa
            'result_count': m_result_count.sum,
            'search_count': search_count,
            'error_count': counter_storage.get(engine_name, 'search', 'count', 'error'),
            'score': score,
            'score_per_result': score_per_result
            }

        stat['time_total_detail'] = measure_storage.get(engine_name, 'time', 'total').quartile_percentage

        max_error = max(max_error, stat['error_count'])
        max_score_per_result = max(max_score_per_result, stat['score_per_result'])

        if search_count or stat['error_count'] > 0:
            stats.append(stat)

    # time
    stats_time = sorted(stats, key=itemgetter('time_total'), reverse=True)
    stats_time_detail = {}
    for stat in stats:
        stats_time_detail[stat['name']] = stat['time_total_detail']

    # errors
    engine_error_list = get_engine_errors()
    error_name_replace = {
        'requests.exceptions.ConnectTimeout': 'Timeout',
        'requests.exceptions.ReadTimeout': 'Timeout',
        'requests.exceptions.Timeout': 'Timeout',
    }
    errors = {
        'series': [],
        'series_to_index': {},
        'engines': [],
        'engines_to_index': {},
        'data': []
    }
    for engine_name, engine_errors in engine_error_list.items():
        if engine_name not in errors['engines']:
            errors['engines'].append(engine_name)
            errors['engines_to_index'][engine_name] = len(errors['engines']) - 1
        for info in engine_errors:
            error_name = info['log_message'] or info['exception_classname']
            error_name = error_name_replace.get(error_name, error_name)
            if error_name not in errors['series']:
                errors['series'].append(error_name)
                errors['series_to_index'][error_name] = len(errors['series']) - 1
    errors['data'] = [[0] * len(errors['engines']) for _ in range(len(errors['series']))]
    for engine_name, engine_errors in engine_error_list.items():
        engine_index = errors['engines_to_index'][engine_name]
        for info in engine_errors:
            error_name = info['log_message'] or info['exception_classname']
            error_name = error_name_replace.get(error_name, error_name)
            serie_index = errors['series_to_index'][error_name]
            errors['data'][serie_index][engine_index] += info['percentage']

    # score
    stats_score = []
    max_score_per_result = 0
    for stat in stats:
        max_score_per_result = max(max_score_per_result, stat["score_per_result"])
        stats_score.append([stat["result_count"], stat["score_per_result"], stat["time_total"],
                            stat["name"], stat["score"]])

    stats_score = sorted(stats_score, key=lambda x: x[4], reverse=True)

    if max_score_per_result > 0:
        score_step = max_score_per_result / 630 * 20
    else:
        score_step = 1

    def shift_y(stat, offset, avoid):
        y = stat[1]
        for s in stats_score:
            if s[1] >= y and s != avoid:
                s[1] += offset

    # buble chart : make it readable by avoiding collision between bubles
    # implementation : no merge, x is never changed, only y is adjusted
    # when a collision is found, all (x,y) above are moved to keep the order
    # in other words, that's mean the absolute value y is meaningless,
    # but the order is preserved.
    # collision = nearby x distance < 4 and nearby y < score_step
    # x = result count, y = score per result
    for stat in stats_score:
        restart = True
        # safeguard : no more iteration than the (x,y) count
        maxIter = len(stats_score)
        # for each collision restart all tests, restart until nothing move
        while restart and maxIter > 0:
            restart = False
            maxIter -= 1
            # for each other (x,y), test collision
            # Warning : found only collision where stat is bellow s on y dimension
            for s in stats_score:
                if s != stat:
                    d1 = s[0] - stat[0]
                    d2 = s[1] - stat[1]
                    if (abs(d1) < 10) and d2 < score_step * 2 and d2 >= 0:
                        # collision found (stat is above)
                        # move all (x,y) above stat to avoid collision
                        shift_y(s, score_step * 3, stat)
                        # everything may has changed : restart
                        restart = True
                        break

    # return result
    return {
        'title_search_page': gettext('Search page'),
        'ticks_search_time': [float(x + 1) / 10
                              for x in range(0, len(measure_storage.get('webapp', 'time', 'search').quartiles))],
        'search_time': {
            'labels': {
                'title': gettext('Total server time'),
                'xaxis': gettext('Time (sec)'),
                'yaxis': gettext('Percentage of requests')
            },
            'values': measure_storage.get('webapp', 'time', 'search').quartile_percentage,
            'average': round(measure_storage.get('webapp', 'time', 'search').average, 3)
        },
        'time': {
            'labels': {
                'title': gettext('Page loads (sec)'),
                'xaxis': gettext('Page loads (sec)'),
                'serie_total': gettext('Total time (sec)'),
                'serie_http': gettext('HTTP time (sec)'),
                'serie_nohttp': gettext('Processing time (sec)')
            },
            'engine': [e.get('name') for e in stats_time],
            'total': [e.get('time_total') for e in stats_time],
            'http': [e.get('time_http') for e in stats_time],
            'nohttp': [e.get('time_total') - e.get('time_http') for e in stats_time],
            'detail': stats_time_detail,
            'height': len(stats) * 1.6 + 5
        },
        'error': {
            'labels': {
                'title': gettext('Errors'),
                'xaxis': gettext('Error percentage'),
                'series': errors['series'],
            },
            'engines': errors['engines'],
            'data': errors['data'],
            'height': len(errors['engines']) * 1.6 + 5
        },
        'score': {
            'labels': {
                'title': gettext('Scores'),
                'xaxis': gettext('Number of results'),
                'yaxis': gettext('Scores per result')
            },
            'stat': stats_score
        },
        'count': len(stats)
    }
