# SPDX-License-Identifier: AGPL-3.0-or-later

import typing
import math
import contextlib
from timeit import default_timer
from operator import itemgetter

from searx.engines import engines
from .models import HistogramStorage, CounterStorage
from .error_recorder import count_error, count_exception, errors_per_engines

__all__ = ["initialize",
           "get_engines_stats", "get_engine_errors",
           "histogram", "histogram_observe", "histogram_observe_time",
           "counter", "counter_inc", "counter_add",
           "count_error", "count_exception"]


ENDPOINTS = {'search'}


histogram_storage: typing.Optional[HistogramStorage] = None
counter_storage: typing.Optional[CounterStorage] = None


@contextlib.contextmanager
def histogram_observe_time(*args):
    h = histogram_storage.get(*args)
    before = default_timer()
    yield before
    duration = default_timer() - before
    if h:
        h.observe(duration)
    else:
        raise ValueError("histogram " + repr((*args,)) + " doesn't not exist")


def histogram_observe(duration, *args):
    histogram_storage.get(*args).observe(duration)


def histogram(*args, raise_on_not_found=True):
    h = histogram_storage.get(*args)
    if raise_on_not_found and h is None:
        raise ValueError("histogram " + repr((*args,)) + " doesn't not exist")
    return h


def counter_inc(*args):
    counter_storage.add(1, *args)


def counter_add(value, *args):
    counter_storage.add(value, *args)


def counter(*args):
    return counter_storage.get(*args)


def initialize(engine_names=None):
    """
    Initialize metrics
    """
    global counter_storage, histogram_storage

    counter_storage = CounterStorage()
    histogram_storage = HistogramStorage()

    # max_timeout = max of all the engine.timeout
    max_timeout = 2
    for engine_name in (engine_names or engines):
        if engine_name in engines:
            max_timeout = max(max_timeout, engines[engine_name].timeout)

    # histogram configuration
    histogram_width = 0.1
    histogram_size = int(1.5 * max_timeout / histogram_width)

    # engines
    for engine_name in (engine_names or engines):
        # search count
        counter_storage.configure('engine', engine_name, 'search', 'count', 'sent')
        counter_storage.configure('engine', engine_name, 'search', 'count', 'successful')
        # global counter of errors
        counter_storage.configure('engine', engine_name, 'search', 'count', 'error')
        # score of the engine
        counter_storage.configure('engine', engine_name, 'score')
        # result count per requests
        histogram_storage.configure(1, 100, 'engine', engine_name, 'result', 'count')
        # time doing HTTP requests
        histogram_storage.configure(histogram_width, histogram_size, 'engine', engine_name, 'time', 'http')
        # total time
        # .time.request and ...response times may overlap .time.http time.
        histogram_storage.configure(histogram_width, histogram_size, 'engine', engine_name, 'time', 'total')


def get_engine_errors(engline_list):
    result = {}
    engine_names = list(errors_per_engines.keys())
    engine_names.sort()
    for engine_name in engine_names:
        if engine_name not in engline_list:
            continue

        error_stats = errors_per_engines[engine_name]
        sent_search_count = max(counter('engine', engine_name, 'search', 'count', 'sent'), 1)
        sorted_context_count_list = sorted(error_stats.items(), key=lambda context_count: context_count[1])
        r = []
        for context, count in sorted_context_count_list:
            percentage = round(20 * count / sent_search_count) * 5
            r.append({
                'filename': context.filename,
                'function': context.function,
                'line_no': context.line_no,
                'code': context.code,
                'exception_classname': context.exception_classname,
                'log_message': context.log_message,
                'log_parameters': context.log_parameters,
                'secondary': context.secondary,
                'percentage': percentage,
            })
        result[engine_name] = sorted(r, reverse=True, key=lambda d: d['percentage'])
    return result


def to_percentage(stats, maxvalue):
    for engine_stat in stats:
        if maxvalue:
            engine_stat['percentage'] = int(engine_stat['avg'] / maxvalue * 100)
        else:
            engine_stat['percentage'] = 0
    return stats


def get_engines_stats(engine_list):
    global counter_storage, histogram_storage

    assert counter_storage is not None
    assert histogram_storage is not None

    list_time = []
    list_time_http = []
    list_time_total = []
    list_result_count = []
    list_error_count = []
    list_scores = []
    list_scores_per_result = []

    max_error_count = max_http_time = max_time_total = max_result_count = max_score = None  # noqa
    for engine_name in engine_list:
        error_count = counter('engine', engine_name, 'search', 'count', 'error')

        if counter('engine', engine_name, 'search', 'count', 'sent') > 0:
            list_error_count.append({'avg': error_count, 'name': engine_name})
            max_error_count = max(error_count, max_error_count or 0)

        successful_count = counter('engine', engine_name, 'search', 'count', 'successful')
        if successful_count == 0:
            continue

        result_count_sum = histogram('engine', engine_name, 'result', 'count').sum
        time_total = histogram('engine', engine_name, 'time', 'total').percentage(50)
        time_http = histogram('engine', engine_name, 'time', 'http').percentage(50)
        result_count = result_count_sum / float(successful_count)

        if result_count:
            score = counter('engine', engine_name, 'score')  # noqa
            score_per_result = score / float(result_count_sum)
        else:
            score = score_per_result = 0.0

        max_time_total = max(time_total, max_time_total or 0)
        max_http_time = max(time_http, max_http_time or 0)
        max_result_count = max(result_count, max_result_count or 0)
        max_score = max(score, max_score or 0)

        list_time.append({'total': round(time_total, 1),
                          'http': round(time_http, 1),
                          'name': engine_name,
                          'processing': round(time_total - time_http, 1)})
        list_time_total.append({'avg': time_total, 'name': engine_name})
        list_time_http.append({'avg': time_http, 'name': engine_name})
        list_result_count.append({'avg': result_count, 'name': engine_name})
        list_scores.append({'avg': score, 'name': engine_name})
        list_scores_per_result.append({'avg': score_per_result, 'name': engine_name})

    list_time = sorted(list_time, key=itemgetter('total'))
    list_time_total = sorted(to_percentage(list_time_total, max_time_total), key=itemgetter('avg'))
    list_time_http = sorted(to_percentage(list_time_http, max_http_time), key=itemgetter('avg'))
    list_result_count = sorted(to_percentage(list_result_count, max_result_count), key=itemgetter('avg'), reverse=True)
    list_scores = sorted(list_scores, key=itemgetter('avg'), reverse=True)
    list_scores_per_result = sorted(list_scores_per_result, key=itemgetter('avg'), reverse=True)
    list_error_count = sorted(to_percentage(list_error_count, max_error_count), key=itemgetter('avg'), reverse=True)

    return {
        'time': list_time,
        'max_time': math.ceil(max_time_total or 0),
        'time_total': list_time_total,
        'time_http': list_time_http,
        'result_count': list_result_count,
        'scores': list_scores,
        'scores_per_result': list_scores_per_result,
        'error_count': list_error_count,
    }
