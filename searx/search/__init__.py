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

import typing
import gc
import threading
from time import time
from uuid import uuid4
from urllib.parse import urlparse
from _thread import start_new_thread

import requests.exceptions
import searx.poolrequests as requests_lib
from searx.engines import engines, settings
from searx.answerers import ask
from searx.external_bang import get_bang_url
from searx.utils import gen_useragent
from searx.results import ResultContainer
from searx import logger
from searx.plugins import plugins
from searx.exceptions import (SearxEngineAccessDeniedException, SearxEngineCaptchaException,
                              SearxEngineTooManyRequestsException,)
from searx.metrology.error_recorder import record_exception, record_error


logger = logger.getChild('search')

max_request_timeout = settings.get('outgoing', {}).get('max_request_timeout' or None)
if max_request_timeout is None:
    logger.info('max_request_timeout={0}'.format(max_request_timeout))
else:
    if isinstance(max_request_timeout, float):
        logger.info('max_request_timeout={0} second(s)'.format(max_request_timeout))
    else:
        logger.critical('outgoing.max_request_timeout if defined has to be float')
        import sys
        sys.exit(1)


class EngineRef:

    __slots__ = 'name', 'category', 'from_bang'

    def __init__(self, name: str, category: str, from_bang: bool=False):
        self.name = name
        self.category = category
        self.from_bang = from_bang

    def __repr__(self):
        return "EngineRef({!r}, {!r}, {!r})".format(self.name, self.category, self.from_bang)

    def __eq__(self, other):
        return self.name == other.name and self.category == other.category and self.from_bang == other.from_bang


class SearchQuery:
    """container for all the search parameters (query, language, etc...)"""

    __slots__ = 'query', 'engineref_list', 'categories', 'lang', 'safesearch', 'pageno', 'time_range',\
                'timeout_limit', 'external_bang'

    def __init__(self,
                 query: str,
                 engineref_list: typing.List[EngineRef],
                 categories: typing.List[str],
                 lang: str,
                 safesearch: int,
                 pageno: int,
                 time_range: typing.Optional[str],
                 timeout_limit: typing.Optional[float]=None,
                 external_bang: typing.Optional[str]=None):
        self.query = query
        self.engineref_list = engineref_list
        self.categories = categories
        self.lang = lang
        self.safesearch = safesearch
        self.pageno = pageno
        self.time_range = time_range
        self.timeout_limit = timeout_limit
        self.external_bang = external_bang

    def __repr__(self):
        return "SearchQuery({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r})".\
               format(self.query, self.engineref_list, self.categories, self.lang, self.safesearch,
                      self.pageno, self.time_range, self.timeout_limit, self.external_bang)

    def __eq__(self, other):
        return self.query == other.query\
            and self.engineref_list == other.engineref_list\
            and self.categories == self.categories\
            and self.lang == other.lang\
            and self.safesearch == other.safesearch\
            and self.pageno == other.pageno\
            and self.time_range == other.time_range\
            and self.timeout_limit == other.timeout_limit\
            and self.external_bang == other.external_bang


def send_http_request(engine, request_params):
    # create dictionary which contain all
    # informations about the request
    request_args = dict(
        headers=request_params['headers'],
        cookies=request_params['cookies'],
        verify=request_params['verify'],
        auth=request_params['auth']
    )

    # setting engine based proxies
    if hasattr(engine, 'proxies'):
        request_args['proxies'] = requests_lib.get_proxies(engine.proxies)

    # max_redirects
    max_redirects = request_params.get('max_redirects')
    if max_redirects:
        request_args['max_redirects'] = max_redirects

    # soft_max_redirects
    soft_max_redirects = request_params.get('soft_max_redirects', max_redirects or 0)

    # raise_for_status
    request_args['raise_for_httperror'] = request_params.get('raise_for_httperror', False)

    # specific type of request (GET or POST)
    if request_params['method'] == 'GET':
        req = requests_lib.get
    else:
        req = requests_lib.post

    request_args['data'] = request_params['data']

    # send the request
    response = req(request_params['url'], **request_args)

    # check soft limit of the redirect count
    if len(response.history) > soft_max_redirects:
        # unexpected redirect : record an error
        # but the engine might still return valid results.
        status_code = str(response.status_code or '')
        reason = response.reason or ''
        hostname = str(urlparse(response.url or '').netloc)
        record_error(engine.name,
                     '{} redirects, maximum: {}'.format(len(response.history), soft_max_redirects),
                     (status_code, reason, hostname))

    return response


def search_one_http_request(engine, query, request_params):
    # update request parameters dependent on
    # search-engine (contained in engines folder)
    engine.request(query, request_params)

    # ignoring empty urls
    if request_params['url'] is None:
        return None

    if not request_params['url']:
        return None

    # send request
    response = send_http_request(engine, request_params)

    # parse the response
    response.search_params = request_params
    return engine.response(response)


def search_one_http_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit):
    # set timeout for all HTTP requests
    requests_lib.set_timeout_for_thread(timeout_limit, start_time=start_time)
    # reset the HTTP total time
    requests_lib.reset_time_for_thread()

    #
    engine = engines[engine_name]

    # suppose everything will be alright
    requests_exception = False
    suspended_time = None

    try:
        # send requests and parse the results
        search_results = search_one_http_request(engine, query, request_params)

        # check if the engine accepted the request
        if search_results is not None:
            # yes, so add results
            result_container.extend(engine_name, search_results)

            # update engine time when there is no exception
            engine_time = time() - start_time
            page_load_time = requests_lib.get_time_for_thread()
            result_container.add_timing(engine_name, engine_time, page_load_time)
            with threading.RLock():
                engine.stats['engine_time'] += engine_time
                engine.stats['engine_time_count'] += 1
                # update stats with the total HTTP time
                engine.stats['page_load_time'] += page_load_time
                engine.stats['page_load_count'] += 1
    except Exception as e:
        record_exception(engine_name, e)

        # Timing
        engine_time = time() - start_time
        page_load_time = requests_lib.get_time_for_thread()
        result_container.add_timing(engine_name, engine_time, page_load_time)

        # Record the errors
        with threading.RLock():
            engine.stats['errors'] += 1

        if (issubclass(e.__class__, requests.exceptions.Timeout)):
            result_container.add_unresponsive_engine(engine_name, 'HTTP timeout')
            # requests timeout (connect or read)
            logger.error("engine {0} : HTTP requests timeout"
                         "(search duration : {1} s, timeout: {2} s) : {3}"
                         .format(engine_name, engine_time, timeout_limit, e.__class__.__name__))
            requests_exception = True
        elif (issubclass(e.__class__, requests.exceptions.RequestException)):
            result_container.add_unresponsive_engine(engine_name, 'HTTP error')
            # other requests exception
            logger.exception("engine {0} : requests exception"
                             "(search duration : {1} s, timeout: {2} s) : {3}"
                             .format(engine_name, engine_time, timeout_limit, e))
            requests_exception = True
        elif (issubclass(e.__class__, SearxEngineCaptchaException)):
            result_container.add_unresponsive_engine(engine_name, 'CAPTCHA required')
            logger.exception('engine {0} : CAPTCHA')
            suspended_time = e.suspended_time  # pylint: disable=no-member
        elif (issubclass(e.__class__, SearxEngineTooManyRequestsException)):
            result_container.add_unresponsive_engine(engine_name, 'too many requests')
            logger.exception('engine {0} : Too many requests')
            suspended_time = e.suspended_time  # pylint: disable=no-member
        elif (issubclass(e.__class__, SearxEngineAccessDeniedException)):
            result_container.add_unresponsive_engine(engine_name, 'blocked')
            logger.exception('engine {0} : Searx is blocked')
            suspended_time = e.suspended_time  # pylint: disable=no-member
        else:
            result_container.add_unresponsive_engine(engine_name, 'unexpected crash')
            # others errors
            logger.exception('engine {0} : exception : {1}'.format(engine_name, e))
    else:
        if getattr(threading.current_thread(), '_timeout', False):
            record_error(engine_name, 'Timeout')

    # suspend the engine if there is an HTTP error
    # or suspended_time is defined
    with threading.RLock():
        if requests_exception or suspended_time:
            # update continuous_errors / suspend_end_time
            engine.continuous_errors += 1
            if suspended_time is None:
                suspended_time = min(settings['search']['max_ban_time_on_fail'],
                                     engine.continuous_errors * settings['search']['ban_time_on_fail'])
            engine.suspend_end_time = time() + suspended_time
        else:
            # reset the suspend variables
            engine.continuous_errors = 0
            engine.suspend_end_time = 0


def record_offline_engine_stats_on_error(engine, result_container, start_time):
    engine_time = time() - start_time
    result_container.add_timing(engine.name, engine_time, engine_time)

    with threading.RLock():
        engine.stats['errors'] += 1


def search_one_offline_request(engine, query, request_params):
    return engine.search(query, request_params)


def search_one_offline_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit):
    engine = engines[engine_name]

    try:
        search_results = search_one_offline_request(engine, query, request_params)

        if search_results:
            result_container.extend(engine_name, search_results)

            engine_time = time() - start_time
            result_container.add_timing(engine_name, engine_time, engine_time)
            with threading.RLock():
                engine.stats['engine_time'] += engine_time
                engine.stats['engine_time_count'] += 1

    except ValueError as e:
        record_exception(engine_name, e)
        record_offline_engine_stats_on_error(engine, result_container, start_time)
        logger.exception('engine {0} : invalid input : {1}'.format(engine_name, e))
    except Exception as e:
        record_exception(engine_name, e)
        record_offline_engine_stats_on_error(engine, result_container, start_time)
        result_container.add_unresponsive_engine(engine_name, 'unexpected crash', str(e))
        logger.exception('engine {0} : exception : {1}'.format(engine_name, e))
    else:
        if getattr(threading.current_thread(), '_timeout', False):
            record_error(engine_name, 'Timeout')


def search_one_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit):
    if engines[engine_name].offline:
        return search_one_offline_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit)  # noqa
    return search_one_http_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit)


def search_multiple_requests(requests, result_container, start_time, timeout_limit):
    search_id = uuid4().__str__()

    for engine_name, query, request_params in requests:
        th = threading.Thread(
            target=search_one_request_safe,
            args=(engine_name, query, request_params, result_container, start_time, timeout_limit),
            name=search_id,
        )
        th._timeout = False
        th._engine_name = engine_name
        th.start()

    for th in threading.enumerate():
        if th.name == search_id:
            remaining_time = max(0.0, timeout_limit - (time() - start_time))
            th.join(remaining_time)
            if th.is_alive():
                th._timeout = True
                result_container.add_unresponsive_engine(th._engine_name, 'timeout')
                logger.warning('engine timeout: {0}'.format(th._engine_name))


# get default reqest parameter
def default_request_params():
    return {
        'method': 'GET',
        'headers': {},
        'data': {},
        'url': '',
        'cookies': {},
        'verify': True,
        'auth': None,
        'raise_for_httperror': True
    }


class Search:
    """Search information container"""

    __slots__ = "search_query", "result_container", "start_time", "actual_timeout"

    def __init__(self, search_query):
        # init vars
        super().__init__()
        self.search_query = search_query
        self.result_container = ResultContainer()
        self.start_time = None
        self.actual_timeout = None

    def search_external_bang(self):
        """
        Check if there is a external bang.
        If yes, update self.result_container and return True
        """
        if self.search_query.external_bang:
            self.result_container.redirect_url = get_bang_url(self.search_query)

            # This means there was a valid bang and the
            # rest of the search does not need to be continued
            if isinstance(self.result_container.redirect_url, str):
                return True
        return False

    def search_answerers(self):
        """
        Check if an answer return a result.
        If yes, update self.result_container and return True
        """
        answerers_results = ask(self.search_query)

        if answerers_results:
            for results in answerers_results:
                self.result_container.extend('answer', results)
            return True
        return False

    def _is_accepted(self, engine_name, engine):
        # skip suspended engines
        if engine.suspend_end_time >= time():
            logger.debug('Engine currently suspended: %s', engine_name)
            return False

        # if paging is not supported, skip
        if self.search_query.pageno > 1 and not engine.paging:
            return False

        # if time_range is not supported, skip
        if self.search_query.time_range and not engine.time_range_support:
            return False

        return True

    def _get_params(self, engineref, user_agent):
        if engineref.name not in engines:
            return None, None

        engine = engines[engineref.name]

        if not self._is_accepted(engineref.name, engine):
            return None, None

        # set default request parameters
        request_params = {}
        if not engine.offline:
            request_params = default_request_params()
            request_params['headers']['User-Agent'] = user_agent

            if hasattr(engine, 'language') and engine.language:
                request_params['language'] = engine.language
            else:
                request_params['language'] = self.search_query.lang

            request_params['safesearch'] = self.search_query.safesearch
            request_params['time_range'] = self.search_query.time_range

        request_params['category'] = engineref.category
        request_params['pageno'] = self.search_query.pageno

        with threading.RLock():
            engine.stats['sent_search_count'] += 1

        return request_params, engine.timeout

    # do search-request
    def _get_requests(self):
        # init vars
        requests = []

        # set default useragent
        # user_agent = request.headers.get('User-Agent', '')
        user_agent = gen_useragent()

        # max of all selected engine timeout
        default_timeout = 0

        # start search-reqest for all selected engines
        for engineref in self.search_query.engineref_list:
            # set default request parameters
            request_params, engine_timeout = self._get_params(engineref, user_agent)
            if request_params is None:
                continue

            # append request to list
            requests.append((engineref.name, self.search_query.query, request_params))

            # update default_timeout
            default_timeout = max(default_timeout, engine_timeout)

        # adjust timeout
        actual_timeout = default_timeout
        query_timeout = self.search_query.timeout_limit

        if max_request_timeout is None and query_timeout is None:
            # No max, no user query: default_timeout
            pass
        elif max_request_timeout is None and query_timeout is not None:
            # No max, but user query: From user query except if above default
            actual_timeout = min(default_timeout, query_timeout)
        elif max_request_timeout is not None and query_timeout is None:
            # Max, no user query: Default except if above max
            actual_timeout = min(default_timeout, max_request_timeout)
        elif max_request_timeout is not None and query_timeout is not None:
            # Max & user query: From user query except if above max
            actual_timeout = min(query_timeout, max_request_timeout)

        logger.debug("actual_timeout={0} (default_timeout={1}, ?timeout_limit={2}, max_request_timeout={3})"
                     .format(actual_timeout, default_timeout, query_timeout, max_request_timeout))

        return requests, actual_timeout

    def search_standard(self):
        """
        Update self.result_container, self.actual_timeout
        """
        requests, self.actual_timeout = self._get_requests()

        # send all search-request
        if requests:
            search_multiple_requests(requests, self.result_container, self.start_time, self.actual_timeout)
            start_new_thread(gc.collect, tuple())

        # return results, suggestions, answers and infoboxes
        return True

    # do search-request
    def search(self):
        self.start_time = time()

        if not self.search_external_bang():
            if not self.search_answerers():
                self.search_standard()

        return self.result_container


class SearchWithPlugins(Search):
    """Similar to the Search class but call the plugins."""

    __slots__ = 'ordered_plugin_list', 'request'

    def __init__(self, search_query, ordered_plugin_list, request):
        super().__init__(search_query)
        self.ordered_plugin_list = ordered_plugin_list
        self.request = request

    def search(self):
        if plugins.call(self.ordered_plugin_list, 'pre_search', self.request, self):
            super().search()

        plugins.call(self.ordered_plugin_list, 'post_search', self.request, self)

        results = self.result_container.get_ordered_results()

        for result in results:
            plugins.call(self.ordered_plugin_list, 'on_result', self.request, self, result)

        return self.result_container
