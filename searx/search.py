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
import threading
from thread import start_new_thread
from time import time
from uuid import uuid4
import searx.poolrequests as requests_lib
from searx.engines import (
    categories, engines
)
from searx.answerers import ask
from searx.utils import gen_useragent
from searx.query import RawTextQuery, SearchQuery
from searx.results import ResultContainer
from searx import logger
from searx.plugins import plugins

logger = logger.getChild('search')

number_of_searches = 0


def send_http_request(engine, request_params, timeout_limit):
    response = None
    try:
        # create dictionary which contain all
        # informations about the request
        request_args = dict(
            headers=request_params['headers'],
            cookies=request_params['cookies'],
            timeout=timeout_limit,
            verify=request_params['verify']
        )
        # specific type of request (GET or POST)
        if request_params['method'] == 'GET':
            req = requests_lib.get
        else:
            req = requests_lib.post
            request_args['data'] = request_params['data']

        # for page_load_time stats
        time_before_request = time()

        # send the request
        response = req(request_params['url'], **request_args)

        with threading.RLock():
            # no error : reset the suspend variables
            engine.continuous_errors = 0
            engine.suspend_end_time = 0
            # update stats with current page-load-time
            # only the HTTP request
            engine.stats['page_load_time'] += time() - time_before_request
            engine.stats['page_load_count'] += 1

        # is there a timeout (no parsing in this case)
        timeout_overhead = 0.2  # seconds
        search_duration = time() - request_params['started']
        if search_duration > timeout_limit + timeout_overhead:
            logger.exception('engine timeout on HTTP request:'
                             '{0} (search duration : {1} ms, time-out: {2} )'
                             .format(engine.name, search_duration, timeout_limit))
            with threading.RLock():
                engine.stats['errors'] += 1
            return False

        # everything is ok : return the response
        return response

    except:
        # increase errors stats
        with threading.RLock():
            engine.stats['errors'] += 1
            engine.continuous_errors += 1
            engine.suspend_end_time = time() + min(60, engine.continuous_errors)

        # print engine name and specific error message
        logger.exception('engine crash: {0}'.format(engine.name))
        return False


def search_one_request(engine_name, query, request_params, result_container, timeout_limit):
    engine = engines[engine_name]

    # update request parameters dependent on
    # search-engine (contained in engines folder)
    engine.request(query, request_params)

    # TODO add support of offline engines
    if request_params['url'] is None:
        return False

    # ignoring empty urls
    if not request_params['url']:
        return False

    # send request
    response = send_http_request(engine, request_params, timeout_limit)

    # parse response
    success = None
    if response:
        # parse the response
        response.search_params = request_params
        try:
            search_results = engine.response(response)
        except:
            logger.exception('engine crash: {0}'.format(engine.name))
            search_results = []

        # add results
        for result in search_results:
            result['engine'] = engine.name

        result_container.extend(engine.name, search_results)

        success = True
    else:
        success = False

    with threading.RLock():
        # update stats : total time
        engine.stats['engine_time'] += time() - request_params['started']
        engine.stats['engine_time_count'] += 1

    return success


def search_multiple_requests(requests, result_container, timeout_limit):
    start_time = time()
    search_id = uuid4().__str__()

    for engine_name, query, request_params in requests:
        th = threading.Thread(
            target=search_one_request,
            args=(engine_name, query, request_params, result_container, timeout_limit),
            name=search_id,
        )
        th._engine_name = engine_name
        th.start()

    for th in threading.enumerate():
        if th.name == search_id:
            remaining_time = max(0.0, timeout_limit - (time() - start_time))
            th.join(remaining_time)
            if th.isAlive():
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


def get_search_query_from_webapp(preferences, form):
    query = None
    query_engines = []
    query_categories = []
    query_pageno = 1
    query_lang = 'all'
    query_time_range = None

    # set blocked engines
    disabled_engines = preferences.engines.get_disabled()

    # set specific language if set
    query_lang = preferences.get_value('language')

    # safesearch
    query_safesearch = preferences.get_value('safesearch')

    # TODO better exceptions
    if not form.get('q'):
        raise Exception('noquery')

    # set pagenumber
    pageno_param = form.get('pageno', '1')
    if not pageno_param.isdigit() or int(pageno_param) < 1:
        pageno_param = 1

    query_pageno = int(pageno_param)

    # parse query, if tags are set, which change
    # the serch engine or search-language
    raw_text_query = RawTextQuery(form['q'], disabled_engines)
    raw_text_query.parse_query()

    # set query
    query = raw_text_query.getSearchQuery()

    # set specific language if set on request, query or preferences
    # TODO support search with multible languages
    if len(raw_text_query.languages):
        query_lang = raw_text_query.languages[-1]
    elif 'language' in form:
        query_lang = form.get('language')
    else:
        query_lang = preferences.get_value('language')

    query_time_range = form.get('time_range')

    query_engines = raw_text_query.engines

    # if engines are calculated from query,
    # set categories by using that informations
    if query_engines and raw_text_query.specific:
        query_categories = list(set(engine['category']
                                    for engine in query_engines))

    # otherwise, using defined categories to
    # calculate which engines should be used
    else:
        # set categories/engines
        load_default_categories = True
        for pd_name, pd in form.items():
            if pd_name == 'categories':
                query_categories.extend(categ for categ in map(unicode.strip, pd.split(',')) if categ in categories)
            elif pd_name == 'engines':
                pd_engines = [{'category': engines[engine].categories[0],
                               'name': engine}
                              for engine in map(unicode.strip, pd.split(',')) if engine in engines]
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
                                            for engine in engines))
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

    return SearchQuery(query, query_engines, query_categories,
                       query_lang, query_safesearch, query_pageno, query_time_range)


class Search(object):

    """Search information container"""

    def __init__(self, search_query):
        # init vars
        super(Search, self).__init__()
        self.search_query = search_query
        self.result_container = ResultContainer()

    # do search-request
    def search(self):
        global number_of_searches

        # start time
        start_time = time()

        # answeres ?
        answerers_results = ask(self.search_query)

        if answerers_results:
            for results in answerers_results:
                self.result_container.extend('answer', results)
            return self.result_container

        # init vars
        requests = []

        # increase number of searches
        number_of_searches += 1

        # set default useragent
        # user_agent = request.headers.get('User-Agent', '')
        user_agent = gen_useragent()

        search_query = self.search_query

        # max of all selected engine timeout
        timeout_limit = 0

        # start search-reqest for all selected engines
        for selected_engine in search_query.engines:
            if selected_engine['name'] not in engines:
                continue

            engine = engines[selected_engine['name']]

            # skip suspended engines
            if engine.suspend_end_time >= time():
                logger.debug('Engine currently suspended: %s', selected_engine['name'])
                continue

            # if paging is not supported, skip
            if search_query.pageno > 1 and not engine.paging:
                continue

            # if search-language is set and engine does not
            # provide language-support, skip
            if search_query.lang != 'all' and not engine.language_support:
                continue

            # if time_range is not supported, skip
            if search_query.time_range and not engine.time_range_support:
                continue

            # set default request parameters
            request_params = default_request_params()
            request_params['headers']['User-Agent'] = user_agent
            request_params['category'] = selected_engine['category']
            request_params['started'] = start_time
            request_params['pageno'] = search_query.pageno

            if hasattr(engine, 'language') and engine.language:
                request_params['language'] = engine.language
            else:
                request_params['language'] = search_query.lang

            # 0 = None, 1 = Moderate, 2 = Strict
            request_params['safesearch'] = search_query.safesearch
            request_params['time_range'] = search_query.time_range

            # append request to list
            requests.append((selected_engine['name'], search_query.query.encode('utf-8'), request_params))

            # update timeout_limit
            timeout_limit = max(timeout_limit, engine.timeout)

        if requests:
            # send all search-request
            search_multiple_requests(requests, self.result_container, timeout_limit - (time() - start_time))
            start_new_thread(gc.collect, tuple())

        # return results, suggestions, answers and infoboxes
        return self.result_container


class SearchWithPlugins(Search):

    """Similar to the Search class but call the plugins."""

    def __init__(self, search_query, request):
        super(SearchWithPlugins, self).__init__(search_query)
        self.request = request

    def search(self):
        if plugins.call('pre_search', self.request, self):
            super(SearchWithPlugins, self).search()

        plugins.call('post_search', self.request, self)

        results = self.result_container.get_ordered_results()

        for result in results:
            plugins.call('on_result', self.request, self, result)

        return self.result_container
