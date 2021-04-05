# SPDX-License-Identifier: AGPL-3.0-or-later

from time import time
import threading
import asyncio

import httpx

import searx.network
from searx.engines import settings
from searx import logger
from searx.utils import gen_useragent
from searx.exceptions import (SearxEngineAccessDeniedException, SearxEngineCaptchaException,
                              SearxEngineTooManyRequestsException,)
from searx.metrology.error_recorder import record_exception, record_error

from searx.search.processors.abstract import EngineProcessor


logger = logger.getChild('search.processor.online')


def default_request_params():
    return {
        'method': 'GET',
        'headers': {},
        'data': {},
        'url': '',
        'cookies': {},
        'verify': True,
        'auth': None
    }


class OnlineProcessor(EngineProcessor):

    engine_type = 'online'

    def get_params(self, search_query, engine_category):
        params = super().get_params(search_query, engine_category)
        if params is None:
            return None

        # skip suspended engines
        if self.engine.suspend_end_time >= time():
            logger.debug('Engine currently suspended: %s', self.engine_name)
            return None

        # add default params
        params.update(default_request_params())

        # add an user agent
        params['headers']['User-Agent'] = gen_useragent()

        return params

    def _send_http_request(self, params):
        # create dictionary which contain all
        # informations about the request
        request_args = dict(
            headers=params['headers'],
            cookies=params['cookies'],
            verify=params['verify'],
            auth=params['auth']
        )

        # max_redirects
        max_redirects = params.get('max_redirects')
        if max_redirects:
            request_args['max_redirects'] = max_redirects

        # allow_redirects
        if 'allow_redirects' in params:
            request_args['allow_redirects'] = params['allow_redirects']

        # soft_max_redirects
        soft_max_redirects = params.get('soft_max_redirects', max_redirects or 0)

        # raise_for_status
        request_args['raise_for_httperror'] = params.get('raise_for_httperror', True)

        # specific type of request (GET or POST)
        if params['method'] == 'GET':
            req = searx.network.get
        else:
            req = searx.network.post

        request_args['data'] = params['data']

        # send the request
        response = req(params['url'], **request_args)

        # check soft limit of the redirect count
        if len(response.history) > soft_max_redirects:
            # unexpected redirect : record an error
            # but the engine might still return valid results.
            status_code = str(response.status_code or '')
            reason = response.reason_phrase or ''
            hostname = response.url.host
            record_error(self.engine_name,
                         '{} redirects, maximum: {}'.format(len(response.history), soft_max_redirects),
                         (status_code, reason, hostname))

        return response

    def _search_basic(self, query, params):
        # update request parameters dependent on
        # search-engine (contained in engines folder)
        self.engine.request(query, params)

        # ignoring empty urls
        if params['url'] is None:
            return None

        if not params['url']:
            return None

        # send request
        response = self._send_http_request(params)

        # parse the response
        response.search_params = params
        return self.engine.response(response)

    def search(self, query, params, result_container, start_time, timeout_limit):
        # set timeout for all HTTP requests
        searx.network.set_timeout_for_thread(timeout_limit, start_time=start_time)
        # reset the HTTP total time
        searx.network.reset_time_for_thread()
        # set the network
        searx.network.set_context_network_name(self.engine_name)

        # suppose everything will be alright
        http_exception = False
        suspended_time = None

        try:
            # send requests and parse the results
            search_results = self._search_basic(query, params)

            # check if the engine accepted the request
            if search_results is not None:
                # yes, so add results
                result_container.extend(self.engine_name, search_results)

                # update engine time when there is no exception
                engine_time = time() - start_time
                page_load_time = searx.network.get_time_for_thread()
                result_container.add_timing(self.engine_name, engine_time, page_load_time)
                with threading.RLock():
                    self.engine.stats['engine_time'] += engine_time
                    self.engine.stats['engine_time_count'] += 1
                    # update stats with the total HTTP time
                    self.engine.stats['page_load_time'] += page_load_time
                    self.engine.stats['page_load_count'] += 1
        except Exception as e:
            record_exception(self.engine_name, e)

            # Timing
            engine_time = time() - start_time
            page_load_time = searx.network.get_time_for_thread()
            result_container.add_timing(self.engine_name, engine_time, page_load_time)

            # Record the errors
            with threading.RLock():
                self.engine.stats['errors'] += 1

            if (issubclass(e.__class__, (httpx.TimeoutException, asyncio.TimeoutError))):
                result_container.add_unresponsive_engine(self.engine_name, 'HTTP timeout')
                # requests timeout (connect or read)
                logger.error("engine {0} : HTTP requests timeout"
                             "(search duration : {1} s, timeout: {2} s) : {3}"
                             .format(self.engine_name, engine_time, timeout_limit, e.__class__.__name__))
                http_exception = True
            elif (issubclass(e.__class__, (httpx.HTTPError, httpx.StreamError))):
                result_container.add_unresponsive_engine(self.engine_name, 'HTTP error')
                # other requests exception
                logger.exception("engine {0} : requests exception"
                                 "(search duration : {1} s, timeout: {2} s) : {3}"
                                 .format(self.engine_name, engine_time, timeout_limit, e))
                http_exception = True
            elif (issubclass(e.__class__, SearxEngineCaptchaException)):
                result_container.add_unresponsive_engine(self.engine_name, 'CAPTCHA required')
                logger.exception('engine {0} : CAPTCHA'.format(self.engine_name))
                suspended_time = e.suspended_time  # pylint: disable=no-member
            elif (issubclass(e.__class__, SearxEngineTooManyRequestsException)):
                result_container.add_unresponsive_engine(self.engine_name, 'too many requests')
                logger.exception('engine {0} : Too many requests'.format(self.engine_name))
                suspended_time = e.suspended_time  # pylint: disable=no-member
            elif (issubclass(e.__class__, SearxEngineAccessDeniedException)):
                result_container.add_unresponsive_engine(self.engine_name, 'blocked')
                logger.exception('engine {0} : Searx is blocked'.format(self.engine_name))
                suspended_time = e.suspended_time  # pylint: disable=no-member
            else:
                result_container.add_unresponsive_engine(self.engine_name, 'unexpected crash')
                # others errors
                logger.exception('engine {0} : exception : {1}'.format(self.engine_name, e))
        else:
            if getattr(threading.current_thread(), '_timeout', False):
                record_error(self.engine_name, 'Timeout')

        # suspend the engine if there is an HTTP error
        # or suspended_time is defined
        with threading.RLock():
            if http_exception or suspended_time:
                # update continuous_errors / suspend_end_time
                self.engine.continuous_errors += 1
                if suspended_time is None:
                    suspended_time = min(settings['search']['max_ban_time_on_fail'],
                                         self.engine.continuous_errors * settings['search']['ban_time_on_fail'])
                self.engine.suspend_end_time = time() + suspended_time
            else:
                # reset the suspend variables
                self.engine.continuous_errors = 0
                self.engine.suspend_end_time = 0

    def get_default_tests(self):
        tests = {}

        tests['simple'] = {
            'matrix': {'query': ('life', 'computer')},
            'result_container': ['not_empty'],
        }

        if getattr(self.engine, 'paging', False):
            tests['paging'] = {
                'matrix': {'query': 'time',
                           'pageno': (1, 2, 3)},
                'result_container': ['not_empty'],
                'test': ['unique_results']
            }
            if 'general' in self.engine.categories:
                # avoid documentation about HTML tags (<time> and <input type="time">)
                tests['paging']['matrix']['query'] = 'news'

        if getattr(self.engine, 'time_range', False):
            tests['time_range'] = {
                'matrix': {'query': 'news',
                           'time_range': (None, 'day')},
                'result_container': ['not_empty'],
                'test': ['unique_results']
            }

        if getattr(self.engine, 'supported_languages', []):
            tests['lang_fr'] = {
                'matrix': {'query': 'paris', 'lang': 'fr'},
                'result_container': ['not_empty', ('has_language', 'fr')],
            }
            tests['lang_en'] = {
                'matrix': {'query': 'paris', 'lang': 'en'},
                'result_container': ['not_empty', ('has_language', 'en')],
            }

        if getattr(self.engine, 'safesearch', False):
            tests['safesearch'] = {
                'matrix': {'query': 'porn',
                           'safesearch': (0, 2)},
                'test': ['unique_results']
            }

        return tests
