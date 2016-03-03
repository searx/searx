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

import threading
import searx.poolrequests as requests_lib
from time import time
from searx import settings
from searx.engines import (
    categories, engines
)
from searx.languages import language_codes
from searx.utils import gen_useragent, get_blocked_engines
from searx.query import Query
from searx.results import ResultContainer
from searx import logger

logger = logger.getChild('search')

number_of_searches = 0


def send_request(engine, request_params, timeout_limit):
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

        response = req(request_params['url'], **request_args)

        search_duration = time() - request_params['started']

        with threading.RLock():
            engine.continuous_errors = 0
            engine.suspend_end_time = 0
            # update stats with current page-load-time
            engine.stats['page_load_time'] += search_duration

        timeout_overhead = 0.2  # seconds
        timeout_limit = engine.timeout + timeout_overhead

        if search_duration > timeout_limit:
            with threading.RLock():
                engine.stats['errors'] += 1
            return False

        return response

    except:
        # increase errors stats
        with threading.RLock():
            engine.stats['errors'] += 1
            engine.continuous_errors += 1
            engine.suspend_end_time = time() + min(60, engine.continuous_errors)

        # print engine name and specific error message
        logger.exception('engine crash: {0}'.format(engine_name))
        return False


def parse_response(engine, request_params, response, result_container):
    # parse the response
    response.search_params = request_params
    search_results = engine.response(response)

    # add results
    for result in search_results:
        result['engine'] = engine.name

    result_container.extend(engine.name, search_results)


def search_request_wrapper(query, engine_name, request_params, timeout_limit, result_container):
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
    response = send_request(engine, request_params, timeout_limit)

    # parse response
    if response:
        parse_response(engine, request_params, response, result_container)
        return True
    else:
        return False


def threaded_requests(requests, timeout_limit, result_container, start_time=None):
    if start_time is None:
        start_time = time()

    for query, request_params, engine_name in requests:
        th = threading.Thread(
            target=search_request_wrapper,
            args=(query, engine_name, request_params, timeout_limit, result_container),
            name='search_request',
        )
        th._engine_name = engine_name
        th.start()

    for th in threading.enumerate():
        if th.name == 'search_request':
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


class Search(object):

    """Search information container"""

    def __init__(self, request):
        # init vars
        super(Search, self).__init__()
        self.query = None
        self.engines = []
        self.categories = []
        self.paging = False
        self.pageno = 1
        self.lang = 'all'

        # set blocked engines
        self.blocked_engines = get_blocked_engines(engines, request.cookies)

        self.result_container = ResultContainer()
        self.request_data = {}

        # set specific language if set
        if request.cookies.get('language')\
           and request.cookies['language'] in (x[0] for x in language_codes):
            self.lang = request.cookies['language']

        # set request method
        if request.method == 'POST':
            self.request_data = request.form
        else:
            self.request_data = request.args

        # TODO better exceptions
        if not self.request_data.get('q'):
            raise Exception('noquery')

        # set pagenumber
        pageno_param = self.request_data.get('pageno', '1')
        if not pageno_param.isdigit() or int(pageno_param) < 1:
            pageno_param = 1

        self.pageno = int(pageno_param)

        # parse query, if tags are set, which change
        # the serch engine or search-language
        query_obj = Query(self.request_data['q'], self.blocked_engines)
        query_obj.parse_query()

        # set query
        self.query = query_obj.getSearchQuery()

        # get last selected language in query, if possible
        # TODO support search with multible languages
        if len(query_obj.languages):
            self.lang = query_obj.languages[-1]

        self.engines = query_obj.engines

        self.categories = []

        # if engines are calculated from query,
        # set categories by using that informations
        if self.engines and query_obj.specific:
            self.categories = list(set(engine['category']
                                       for engine in self.engines))

        # otherwise, using defined categories to
        # calculate which engines should be used
        else:
            # set categories/engines
            load_default_categories = True
            for pd_name, pd in self.request_data.items():
                if pd_name == 'categories':
                    self.categories.extend(categ for categ in map(unicode.strip, pd.split(',')) if categ in categories)
                elif pd_name == 'engines':
                    pd_engines = [{'category': engines[engine].categories[0],
                                   'name': engine}
                                  for engine in map(unicode.strip, pd.split(',')) if engine in engines]
                    if pd_engines:
                        self.engines.extend(pd_engines)
                        load_default_categories = False
                elif pd_name.startswith('category_'):
                    category = pd_name[9:]

                    # if category is not found in list, skip
                    if category not in categories:
                        continue

                    if pd != 'off':
                        # add category to list
                        self.categories.append(category)
                    elif category in self.categories:
                        # remove category from list if property is set to 'off'
                        self.categories.remove(category)

            if not load_default_categories:
                if not self.categories:
                    self.categories = list(set(engine['category']
                                               for engine in self.engines))
                return

            # if no category is specified for this search,
            # using user-defined default-configuration which
            # (is stored in cookie)
            if not self.categories:
                cookie_categories = request.cookies.get('categories', '')
                cookie_categories = cookie_categories.split(',')
                for ccateg in cookie_categories:
                    if ccateg in categories:
                        self.categories.append(ccateg)

            # if still no category is specified, using general
            # as default-category
            if not self.categories:
                self.categories = ['general']

            # using all engines for that search, which are
            # declared under the specific categories
            for categ in self.categories:
                self.engines.extend({'category': categ,
                                     'name': engine.name}
                                    for engine in categories[categ]
                                    if (engine.name, categ) not in self.blocked_engines)

        # remove suspended engines
        self.engines = [e for e in self.engines
                        if engines[e['name']].suspend_end_time <= time()]

    # do search-request
    def search(self, request):
        global number_of_searches

        # start time
        start_time = time()

        # init vars
        requests = []

        # increase number of searches
        number_of_searches += 1

        # set default useragent
        # user_agent = request.headers.get('User-Agent', '')
        user_agent = gen_useragent()

        # max of all selected engine timeout
        timeout_limit = 0

        # start search-reqest for all selected engines
        for selected_engine in self.engines:
            if selected_engine['name'] not in engines:
                continue

            engine = engines[selected_engine['name']]

            # if paging is not supported, skip
            if self.pageno > 1 and not engine.paging:
                continue

            # if search-language is set and engine does not
            # provide language-support, skip
            if self.lang != 'all' and not engine.language_support:
                continue

            # set default request parameters
            request_params = default_request_params()
            request_params['headers']['User-Agent'] = user_agent
            request_params['category'] = selected_engine['category']
            request_params['started'] = start_time
            request_params['pageno'] = self.pageno

            if hasattr(engine, 'language') and engine.language:
                request_params['language'] = engine.language
            else:
                request_params['language'] = self.lang

            try:
                # 0 = None, 1 = Moderate, 2 = Strict
                request_params['safesearch'] = int(request.cookies.get('safesearch'))
            except Exception:
                request_params['safesearch'] = settings['search']['safe_search']

            # append request to list
            requests.append((self.query.encode('utf-8'), request_params, selected_engine['name']))

            # update timeout_limit
            timeout_limit = max(timeout_limit, engine.timeout)

        if not requests:
            return self
        # send all search-request
        threaded_requests(requests, timeout_limit, self.result_container, start_time=start_time)

        # return results, suggestions, answers and infoboxes
        return self
