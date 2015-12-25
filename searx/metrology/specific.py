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

(C) 2015- by Alexandre Flament, <alex@al-f.net>
'''

from operator import itemgetter
from flask.ext.babel import gettext
from searx.engines import engines
import searx.metrology as metrology


def initialize():
    # initialize metrology
    # response time of a search (everything)
    metrology.configure_measure(0.1, 30, 'search', 'time')
    # response time of a search, without rendering
    metrology.configure_measure(0.1, 30, 'search', 'time', 'search')
    # response time of a search, only rendering
    metrology.configure_measure(0.1, 30, 'search', 'time', 'render')
    for engine in engines:
        # result count per requests
        metrology.configure_measure(1, 100, engine, 'result', 'count')
        # time for calling the "request" function
        metrology.configure_measure(0.1, 30, engine, 'time', 'request')
        # time for the HTTP(S) request
        metrology.configure_measure(0.1, 30, engine, 'time', 'search')
        # time for calling the callback function "response"
        # call everytime, even if the callback hasn't really call 
        # to keep the call count synchronize with <engine>, time, search
        metrology.configure_measure(0.1, 30, engine, 'time', 'callback')
        # time to append the results
        # call everytime, even if the callback hasn't really call 
        # to keep the call count synchronize with <engine>, time, search
        metrology.configure_measure(0.1, 30, engine, 'time', 'append')
        # global time (request, search, callback, append)
        # call everytime, even if the callback hasn't really call 
        # to keep the call count synchronize with <engine>, time, search
        metrology.configure_measure(0.1, 30, engine, 'time', 'total')
        # bandwidth usage (from searx to outside), update for each HTTP request
        # warning : not used
        metrology.configure_measure(1024, 300, engine, 'bandwidth', 'up')
        # bandwidth usage (from outside to searx), uddate for each HTTP request
        # warning : only the bytes from the main requests,
        # an engine can make several HTTP requests per user request
        metrology.configure_measure(1024, 300, engine, 'bandwidth', 'down')
        # score of the engine
        metrology.reset_counter(engine, 'score')
        # count the number of timeout
        metrology.reset_counter(engine, 'error', 'timeout')
        # count the number of requests lib errors
        metrology.reset_counter(engine, 'error', 'requests')
        # count the other errors
        metrology.reset_counter(engine, 'error', 'other')
        # global counter of errors
        metrology.reset_counter(engine, 'error')


def get_engines_stats():
    # TODO refactor
    pageloads = []
    results = []
    scores = []
    errors = []
    scores_per_result = []

    max_pageload = max_results = max_score = max_errors = max_score_per_result = 0  # noqa

    for engine in engines.values():
        error_count = metrology.counter(engine.name, 'error')
        if error_count > 0:
            max_errors = max(max_errors, error_count)
            errors.append({'avg': error_count, 'name': engine.name})

    for engine in engines.values():
        m_result_count = metrology.measure(engine.name, 'result', 'count')
        if m_result_count.get_count() == 0:
            continue
        m_time_total = metrology.measure(engine.name, 'time', 'total')
        score_count = metrology.counter(engine.name, 'score')

        result_count_avg = m_result_count.get_average()
        search_count = m_result_count.get_count()
        time_total_avg = m_time_total.get_average()  # noqa
        if search_count > 0 and result_count_avg > 0:
            score = score_count / float(search_count)  # noqa
            score_per_result = score / result_count_avg
        else:
            score = score_per_result = 0.0
        max_results = max(result_count_avg, max_results)
        max_pageload = max(time_total_avg, max_pageload)
        max_score = max(score, max_score)
        max_score_per_result = max(score_per_result, max_score_per_result)
        pageloads.append({'avg': time_total_avg, 'name': engine.name})
        results.append({'avg': result_count_avg, 'name': engine.name})
        scores.append({'avg': score, 'name': engine.name})
        scores_per_result.append({
            'avg': score_per_result,
            'name': engine.name
        })

    for engine in pageloads:
        if max_pageload:
            engine['percentage'] = int(engine['avg'] / max_pageload * 100)
        else:
            engine['percentage'] = 0

    for engine in results:
        if max_results:
            engine['percentage'] = int(engine['avg'] / max_results * 100)
        else:
            engine['percentage'] = 0

    for engine in scores:
        if max_score:
            engine['percentage'] = int(engine['avg'] / max_score * 100)
        else:
            engine['percentage'] = 0

    for engine in scores_per_result:
        if max_score_per_result:
            engine['percentage'] = int(engine['avg']
                                       / max_score_per_result * 100)
        else:
            engine['percentage'] = 0

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
