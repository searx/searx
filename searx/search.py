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

import gc
import sys
import threading
from time import time
from uuid import uuid4
from _thread import start_new_thread

from flask_babel import gettext
import requests.exceptions
import searx.poolrequests as requests_lib
from searx.engines import (
    categories, engines, settings
)
from searx.answerers import ask
from searx.external_bang import get_bang_url
from searx.utils import gen_useragent
from searx.query import RawTextQuery, SearchQuery, VALID_LANGUAGE_CODE
from searx.results import ResultContainer
from searx import logger
from searx.plugins import plugins
from searx.exceptions import SearxParameterException


logger = logger.getChild('search')

number_of_searches = 0
max_request_timeout = settings.get('outgoing', {}).get('max_request_timeout' or None)
if max_request_timeout is None:
    logger.info('max_request_timeout={0}'.format(max_request_timeout))
else:
    if isinstance(max_request_timeout, float):
        logger.info('max_request_timeout={0} second(s)'.format(max_request_timeout))
    else:
        logger.critical('outgoing.max_request_timeout if defined has to be float')
        from sys import exit

        exit(1)


def send_http_request(engine, request_params):
    # create dictionary which contain all
    # informations about the request
    request_args = dict(
        headers=request_params['headers'],
        cookies=request_params['cookies'],
        verify=request_params['verify']
    )

    # setting engine based proxies
    if hasattr(engine, 'proxies'):
        request_args['proxies'] = engine.proxies

    # specific type of request (GET or POST)
    if request_params['method'] == 'GET':
        req = requests_lib.get
    else:
        req = requests_lib.post
        request_args['data'] = request_params['data']

    # send the request
    return req(request_params['url'], **request_args)


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


def search_one_offline_request(engine, query, request_params):
    return engine.search(query, request_params)


def search_one_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit):
    if engines[engine_name].offline:
        return search_one_offline_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit)  # noqa
    return search_one_http_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit)


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
        record_offline_engine_stats_on_error(engine, result_container, start_time)
        logger.exception('engine {0} : invalid input : {1}'.format(engine_name, e))
    except Exception as e:
        record_offline_engine_stats_on_error(engine, result_container, start_time)
        result_container.add_unresponsive_engine(engine_name, 'unexpected crash', str(e))
        logger.exception('engine {0} : exception : {1}'.format(engine_name, e))


def record_offline_engine_stats_on_error(engine, result_container, start_time):
    engine_time = time() - start_time
    result_container.add_timing(engine.name, engine_time, engine_time)

    with threading.RLock():
        engine.stats['errors'] += 1


def search_one_http_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit):
    # set timeout for all HTTP requests
    requests_lib.set_timeout_for_thread(timeout_limit, start_time=start_time)
    # reset the HTTP total time
    requests_lib.reset_time_for_thread()

    #
    engine = engines[engine_name]

    # suppose everything will be alright
    requests_exception = False

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
        # Timing
        engine_time = time() - start_time
        page_load_time = requests_lib.get_time_for_thread()
        result_container.add_timing(engine_name, engine_time, page_load_time)

        # Record the errors
        with threading.RLock():
            engine.stats['errors'] += 1

        if (issubclass(e.__class__, requests.exceptions.Timeout)):
            result_container.add_unresponsive_engine(engine_name, 'timeout')
            # requests timeout (connect or read)
            logger.error("engine {0} : HTTP requests timeout"
                         "(search duration : {1} s, timeout: {2} s) : {3}"
                         .format(engine_name, engine_time, timeout_limit, e.__class__.__name__))
            requests_exception = True
        elif (issubclass(e.__class__, requests.exceptions.RequestException)):
            result_container.add_unresponsive_engine(engine_name, 'request exception')
            # other requests exception
            logger.exception("engine {0} : requests exception"
                             "(search duration : {1} s, timeout: {2} s) : {3}"
                             .format(engine_name, engine_time, timeout_limit, e))
            requests_exception = True
        else:
            result_container.add_unresponsive_engine(engine_name, 'unexpected crash', str(e))
            # others errors
            logger.exception('engine {0} : exception : {1}'.format(engine_name, e))

    # suspend or not the engine if there are HTTP errors
    with threading.RLock():
        if requests_exception:
            # update continuous_errors / suspend_end_time
            engine.continuous_errors += 1
            engine.suspend_end_time = time() + min(settings['search']['max_ban_time_on_fail'],
                                                   engine.continuous_errors * settings['search']['ban_time_on_fail'])
        else:
            # no HTTP error (perhaps an engine error)
            # anyway, reset the suspend variables
            engine.continuous_errors = 0
            engine.suspend_end_time = 0


def search_multiple_requests(requests, result_container, start_time, timeout_limit):
    search_id = uuid4().__str__()

    for engine_name, query, request_params in requests:
        th = threading.Thread(
            target=search_one_request_safe,
            args=(engine_name, query, request_params, result_container, start_time, timeout_limit),
            name=search_id,
        )
        th._engine_name = engine_name
        th.start()

    for th in threading.enumerate():
        if th.name == search_id:
            remaining_time = max(0.0, timeout_limit - (time() - start_time))
            th.join(remaining_time)
            if th.is_alive():
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
        'verify': True
    }


# remove duplicate queries.
# FIXME: does not fix "!music !soundcloud", because the categories are 'none' and 'music'
def deduplicate_query_engines(query_engines):
    uniq_query_engines = {q["category"] + '|' + q["name"]: q for q in query_engines}
    return uniq_query_engines.values()


def get_search_query_from_webapp(preferences, form):
    # no text for the query ?
    if not form.get('q'):
        raise SearxParameterException('q', '')

    # set blocked engines
    disabled_engines = preferences.engines.get_disabled()

    # parse query, if tags are set, which change
    # the serch engine or search-language
    raw_text_query = RawTextQuery(form['q'], disabled_engines)

    # set query
    query = raw_text_query.getSearchQuery()

    # get and check page number
    pageno_param = form.get('pageno', '1')
    if not pageno_param.isdigit() or int(pageno_param) < 1:
        raise SearxParameterException('pageno', pageno_param)
    query_pageno = int(pageno_param)

    # get language
    # set specific language if set on request, query or preferences
    # TODO support search with multible languages
    if len(raw_text_query.languages):
        query_lang = raw_text_query.languages[-1]
    elif 'language' in form:
        query_lang = form.get('language')
    else:
        query_lang = preferences.get_value('language')

    # check language
    if not VALID_LANGUAGE_CODE.match(query_lang):
        raise SearxParameterException('language', query_lang)

    # get safesearch
    if 'safesearch' in form:
        query_safesearch = form.get('safesearch')
        # first check safesearch
        if not query_safesearch.isdigit():
            raise SearxParameterException('safesearch', query_safesearch)
        query_safesearch = int(query_safesearch)
    else:
        query_safesearch = preferences.get_value('safesearch')

    # safesearch : second check
    if query_safesearch < 0 or query_safesearch > 2:
        raise SearxParameterException('safesearch', query_safesearch)

    # get time_range
    query_time_range = form.get('time_range')

    # check time_range
    if query_time_range not in ('None', None, '', 'day', 'week', 'month', 'year'):
        raise SearxParameterException('time_range', query_time_range)

    # query_engines
    query_engines = raw_text_query.engines

    # timeout_limit
    query_timeout = raw_text_query.timeout_limit
    if query_timeout is None and 'timeout_limit' in form:
        raw_time_limit = form.get('timeout_limit')
        if raw_time_limit in ['None', '']:
            raw_time_limit = None
        else:
            try:
                query_timeout = float(raw_time_limit)
            except ValueError:
                raise SearxParameterException('timeout_limit', raw_time_limit)

    # query_categories
    query_categories = []

    # if engines are calculated from query,
    # set categories by using that informations
    if query_engines and raw_text_query.specific:
        additional_categories = set()
        for engine in query_engines:
            if 'from_bang' in engine and engine['from_bang']:
                additional_categories.add('none')
            else:
                additional_categories.add(engine['category'])
        query_categories = list(additional_categories)

    # otherwise, using defined categories to
    # calculate which engines should be used
    else:
        # set categories/engines
        load_default_categories = True
        for pd_name, pd in form.items():
            if pd_name == 'categories':
                query_categories.extend(categ for categ in map(str.strip, pd.split(',')) if categ in categories)
            elif pd_name == 'engines':
                pd_engines = [{'category': engines[engine].categories[0],
                               'name': engine}
                              for engine in map(str.strip, pd.split(',')) if engine in engines]
                if pd_engines:
                    query_engines.extend(pd_engines)
                    load_default_categories = False
            elif pd_name.startswith('category_'):
                category = pd_name[9:]

                # if category is not found in list, skip
                if category not in categories:
                    continue

                if pd != 'off':
                    # add category to list
                    query_categories.append(category)
                elif category in query_categories:
                    # remove category from list if property is set to 'off'
                    query_categories.remove(category)

        if not load_default_categories:
            if not query_categories:
                query_categories = list(set(engine['category']
                                            for engine in query_engines))
        else:
            # if no category is specified for this search,
            # using user-defined default-configuration which
            # (is stored in cookie)
            if not query_categories:
                cookie_categories = preferences.get_value('categories')
                for ccateg in cookie_categories:
                    if ccateg in categories:
                        query_categories.append(ccateg)

            # if still no category is specified, using general
            # as default-category
            if not query_categories:
                query_categories = ['general']

            # using all engines for that search, which are
            # declared under the specific categories
            for categ in query_categories:
                query_engines.extend({'category': categ,
                                      'name': engine.name}
                                     for engine in categories[categ]
                                     if (engine.name, categ) not in disabled_engines)

    query_engines = deduplicate_query_engines(query_engines)
    external_bang = raw_text_query.external_bang

    return (SearchQuery(query, query_engines, query_categories,
                        query_lang, query_safesearch, query_pageno,
                        query_time_range, query_timeout, preferences,
                        external_bang=external_bang),
            raw_text_query)


class Search:
    """Search information container"""

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
        if not self.search_query.preferences.validate_token(engine):
            return False

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

    def _get_params(self, selected_engine, user_agent):
        if selected_engine['name'] not in engines:
            return None, None

        engine = engines[selected_engine['name']]

        if not self._is_accepted(selected_engine['name'], engine):
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

        request_params['category'] = selected_engine['category']
        request_params['pageno'] = self.search_query.pageno

        return request_params, engine.timeout

    # do search-request
    def _get_requests(self):
        global number_of_searches

        # init vars
        requests = []

        # increase number of searches
        number_of_searches += 1

        # set default useragent
        # user_agent = request.headers.get('User-Agent', '')
        user_agent = gen_useragent()

        # max of all selected engine timeout
        default_timeout = 0

        # start search-reqest for all selected engines
        for selected_engine in self.search_query.engines:
            # set default request parameters
            request_params, engine_timeout = self._get_params(selected_engine, user_agent)
            if request_params is None:
                continue

            # append request to list
            requests.append((selected_engine['name'], self.search_query.query, request_params))

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
                     .format(self.actual_timeout, default_timeout, query_timeout, max_request_timeout))

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
