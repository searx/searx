# SPDX-License-Identifier: AGPL-3.0-or-later

from urllib.parse import urlparse
from time import perf_counter
import requests.exceptions

import searx.poolrequests as poolrequests
from searx import logger
from searx.utils import gen_useragent
from searx.exceptions import (SearxEngineAccessDeniedException, SearxEngineCaptchaException,
                              SearxEngineTooManyRequestsException,)
from searx.metrics import count_error
from searx.search.processors.abstract import EngineProcessor


logger = logger.getChild('searx.search.processor.online')


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

        # setting engine based proxies
        if hasattr(self.engine, 'proxies'):
            request_args['proxies'] = poolrequests.get_proxies(self.engine.proxies)

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
            req = poolrequests.get
        else:
            req = poolrequests.post

        request_args['data'] = params['data']

        # send the request
        response = req(params['url'], **request_args)

        # check soft limit of the redirect count
        if len(response.history) > soft_max_redirects:
            # unexpected redirect : record an error
            # but the engine might still return valid results.
            status_code = str(response.status_code or '')
            reason = response.reason or ''
            hostname = str(urlparse(response.url or '').netloc)
            count_error(self.engine_name,
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
        poolrequests.set_timeout_for_thread(timeout_limit, start_time=start_time)
        # reset the HTTP total time
        poolrequests.reset_time_for_thread()

        try:
            # send requests and parse the results
            search_results = self._search_basic(query, params)
            self._extend_container(result_container, start_time, search_results)
        except requests.exceptions.Timeout as e:
            # requests timeout (connect or read)
            self._handle_exception(result_container, 'HTTP timeout', e, suspend=True)
            logger.error("engine {0} : HTTP requests timeout"
                         "(search duration : {1} s, timeout: {2} s) : {3}"
                         .format(self.engine_name, perf_counter() - start_time,
                                 timeout_limit,
                                 e.__class__.__name__))
        except requests.exceptions.RequestException as e:
            # other requests exception
            self._handle_exception(result_container, 'HTTP error', e, suspend=True)
            logger.exception("engine {0} : requests exception"
                             "(search duration : {1} s, timeout: {2} s) : {3}"
                             .format(self.engine_name, perf_counter() - start_time,
                                     timeout_limit,
                                     e))
        except SearxEngineCaptchaException as e:
            self._handle_exception(result_container, 'CAPTCHA required', e, suspend=True)
            logger.exception('engine {0} : CAPTCHA'.format(self.engine_name))
        except SearxEngineTooManyRequestsException as e:
            self._handle_exception(result_container, 'too many requests', e, suspend=True)
            logger.exception('engine {0} : Too many requests'.format(self.engine_name))
        except SearxEngineAccessDeniedException as e:
            self._handle_exception(result_container, 'blocked', e, suspend=True)
            logger.exception('engine {0} : Searx is blocked'.format(self.engine_name))
        except Exception as e:
            self._handle_exception(result_container, 'unexpected crash', e)
            logger.exception('engine {0} : exception : {1}'.format(self.engine_name, e))

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
