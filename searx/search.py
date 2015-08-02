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
import re
import searx.poolrequests as requests_lib
from itertools import izip_longest, chain
from operator import itemgetter
from Queue import Queue
from time import time
from urlparse import urlparse, unquote
from searx import settings
from searx.engines import (
    categories, engines
)
from searx.languages import language_codes
from searx.utils import gen_useragent, get_blocked_engines
from searx.query import Query
from searx import logger

logger = logger.getChild('search')

number_of_searches = 0


def search_request_wrapper(fn, url, engine_name, **kwargs):
    try:
        return fn(url, **kwargs)
    except:
        # increase errors stats
        engines[engine_name].stats['errors'] += 1

        # print engine name and specific error message
        logger.exception('engine crash: {0}'.format(engine_name))
        return


def threaded_requests(requests):
    timeout_limit = max(r[2]['timeout'] for r in requests)
    search_start = time()
    for fn, url, request_args, engine_name in requests:
        request_args['timeout'] = timeout_limit
        th = threading.Thread(
            target=search_request_wrapper,
            args=(fn, url, engine_name),
            kwargs=request_args,
            name='search_request',
        )
        th._engine_name = engine_name
        th.start()

    for th in threading.enumerate():
        if th.name == 'search_request':
            remaining_time = max(0.0, timeout_limit - (time() - search_start))
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


# create a callback wrapper for the search engine results
def make_callback(engine_name, results_queue, callback, params):

    # creating a callback wrapper for the search engine results
    def process_callback(response, **kwargs):
        # check if redirect comparing to the True value,
        # because resp can be a Mock object, and any attribut name returns something.
        if response.is_redirect is True:
            logger.debug('{0} redirect on: {1}'.format(engine_name, response))
            return

        response.search_params = params

        timeout_overhead = 0.2  # seconds
        search_duration = time() - params['started']
        timeout_limit = engines[engine_name].timeout + timeout_overhead
        if search_duration > timeout_limit:
            engines[engine_name].stats['page_load_time'] += timeout_limit
            engines[engine_name].stats['errors'] += 1
            return

        # callback
        search_results = callback(response)

        # add results
        for result in search_results:
            result['engine'] = engine_name

        results_queue.put_nowait((engine_name, search_results))

        # update stats with current page-load-time
        engines[engine_name].stats['page_load_time'] += search_duration

    return process_callback


# return the meaningful length of the content for a result
def content_result_len(content):
    if isinstance(content, basestring):
        content = re.sub('[,;:!?\./\\\\ ()-_]', '', content)
        return len(content)
    else:
        return 0


# score results and remove duplications
def score_results(results):
    # calculate scoring parameters
    flat_res = filter(
        None, chain.from_iterable(izip_longest(*results.values())))
    flat_len = len(flat_res)
    engines_len = len(results)

    results = []

    # pass 1: deduplication + scoring
    for i, res in enumerate(flat_res):

        res['parsed_url'] = urlparse(res['url'])

        res['host'] = res['parsed_url'].netloc

        if res['host'].startswith('www.'):
            res['host'] = res['host'].replace('www.', '', 1)

        res['engines'] = [res['engine']]

        weight = 1.0

        # strip multiple spaces and cariage returns from content
        if res.get('content'):
            res['content'] = re.sub(' +', ' ',
                                    res['content'].strip().replace('\n', ''))

        # get weight of this engine if possible
        if hasattr(engines[res['engine']], 'weight'):
            weight = float(engines[res['engine']].weight)

        # calculate score for that engine
        score = int((flat_len - i) / engines_len) * weight + 1

        # check for duplicates
        duplicated = False
        for new_res in results:
            # remove / from the end of the url if required
            p1 = res['parsed_url'].path[:-1]\
                if res['parsed_url'].path.endswith('/')\
                else res['parsed_url'].path
            p2 = new_res['parsed_url'].path[:-1]\
                if new_res['parsed_url'].path.endswith('/')\
                else new_res['parsed_url'].path

            # check if that result is a duplicate
            if res['host'] == new_res['host'] and\
               unquote(p1) == unquote(p2) and\
               res['parsed_url'].query == new_res['parsed_url'].query and\
               res.get('template') == new_res.get('template'):
                duplicated = new_res
                break

        # merge duplicates together
        if duplicated:
            # using content with more text
            if content_result_len(res.get('content', '')) >\
                    content_result_len(duplicated.get('content', '')):
                duplicated['content'] = res['content']

            # increase result-score
            duplicated['score'] += score

            # add engine to list of result-engines
            duplicated['engines'].append(res['engine'])

            # using https if possible
            if duplicated['parsed_url'].scheme == 'https':
                continue
            elif res['parsed_url'].scheme == 'https':
                duplicated['url'] = res['parsed_url'].geturl()
                duplicated['parsed_url'] = res['parsed_url']

        # if there is no duplicate found, append result
        else:
            res['score'] = score
            results.append(res)

    results = sorted(results, key=itemgetter('score'), reverse=True)

    # pass 2 : group results by category and template
    gresults = []
    categoryPositions = {}

    for i, res in enumerate(results):
        # FIXME : handle more than one category per engine
        category = engines[res['engine']].categories[0] + ':' + ''\
            if 'template' not in res\
            else res['template']

        current = None if category not in categoryPositions\
            else categoryPositions[category]

        # group with previous results using the same category
        # if the group can accept more result and is not too far
        # from the current position
        if current is not None and (current['count'] > 0)\
                and (len(gresults) - current['index'] < 20):
            # group with the previous results using
            # the same category with this one
            index = current['index']
            gresults.insert(index, res)

            # update every index after the current one
            # (including the current one)
            for k in categoryPositions:
                v = categoryPositions[k]['index']
                if v >= index:
                    categoryPositions[k]['index'] = v + 1

            # update this category
            current['count'] -= 1

        else:
            # same category
            gresults.append(res)

            # update categoryIndex
            categoryPositions[category] = {'index': len(gresults), 'count': 8}

    # return gresults
    return gresults


def merge_two_infoboxes(infobox1, infobox2):
    if 'urls' in infobox2:
        urls1 = infobox1.get('urls', None)
        if urls1 is None:
            urls1 = []
            infobox1.set('urls', urls1)

        urlSet = set()
        for url in infobox1.get('urls', []):
            urlSet.add(url.get('url', None))

        for url in infobox2.get('urls', []):
            if url.get('url', None) not in urlSet:
                urls1.append(url)

    if 'attributes' in infobox2:
        attributes1 = infobox1.get('attributes', None)
        if attributes1 is None:
            attributes1 = []
            infobox1.set('attributes', attributes1)

        attributeSet = set()
        for attribute in infobox1.get('attributes', []):
            if attribute.get('label', None) not in attributeSet:
                attributeSet.add(attribute.get('label', None))

        for attribute in infobox2.get('attributes', []):
            attributes1.append(attribute)

    if 'content' in infobox2:
        content1 = infobox1.get('content', None)
        content2 = infobox2.get('content', '')
        if content1 is not None:
            if content_result_len(content2) > content_result_len(content1):
                infobox1['content'] = content2
        else:
            infobox1.set('content', content2)


def merge_infoboxes(infoboxes):
    results = []
    infoboxes_id = {}
    for infobox in infoboxes:
        add_infobox = True
        infobox_id = infobox.get('id', None)
        if infobox_id is not None:
            existingIndex = infoboxes_id.get(infobox_id, None)
            if existingIndex is not None:
                merge_two_infoboxes(results[existingIndex], infobox)
                add_infobox = False

        if add_infobox:
            results.append(infobox)
            infoboxes_id[infobox_id] = len(results) - 1

    return results


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

        self.results = []
        self.suggestions = set()
        self.answers = set()
        self.infoboxes = []
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
            raise Exception('wrong pagenumber')

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
                    self.categories.extend(categ.strip() for categ in pd.split(',') if categ in categories)
                elif pd_name == 'engines':
                    pd_engines = [{'category': engines[engine].categories[0],
                                   'name': engine}
                                  for engine in map(str.strip, pd.split(',')) if engine in engines]
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

    # do search-request
    def search(self, request):
        global number_of_searches

        # init vars
        requests = []
        results_queue = Queue()
        results = {}

        # increase number of searches
        number_of_searches += 1

        # set default useragent
        # user_agent = request.headers.get('User-Agent', '')
        user_agent = gen_useragent()

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
            request_params['started'] = time()
            request_params['pageno'] = self.pageno

            if hasattr(engine, 'language'):
                request_params['language'] = engine.language
            else:
                request_params['language'] = self.lang

            try:
                # 0 = None, 1 = Moderate, 2 = Strict
                request_params['safesearch'] = int(request.cookies.get('safesearch'))
            except ValueError:
                request_params['safesearch'] = settings['search']['safe_search']

            # update request parameters dependent on
            # search-engine (contained in engines folder)
            engine.request(self.query.encode('utf-8'), request_params)

            if request_params['url'] is None:
                # TODO add support of offline engines
                pass

            # create a callback wrapper for the search engine results
            callback = make_callback(
                selected_engine['name'],
                results_queue,
                engine.response,
                request_params)

            # create dictionary which contain all
            # informations about the request
            request_args = dict(
                headers=request_params['headers'],
                hooks=dict(response=callback),
                cookies=request_params['cookies'],
                timeout=engine.timeout,
                verify=request_params['verify']
            )

            # specific type of request (GET or POST)
            if request_params['method'] == 'GET':
                req = requests_lib.get
            else:
                req = requests_lib.post
                request_args['data'] = request_params['data']

            # ignoring empty urls
            if not request_params['url']:
                continue

            # append request to list
            requests.append((req, request_params['url'],
                             request_args,
                             selected_engine['name']))

        if not requests:
            return self
        # send all search-request
        threaded_requests(requests)

        while not results_queue.empty():
            engine_name, engine_results = results_queue.get_nowait()

            # TODO type checks
            [self.suggestions.add(x['suggestion'])
             for x in list(engine_results)
             if 'suggestion' in x
             and engine_results.remove(x) is None]

            [self.answers.add(x['answer'])
             for x in list(engine_results)
             if 'answer' in x
             and engine_results.remove(x) is None]

            self.infoboxes.extend(x for x in list(engine_results)
                                  if 'infobox' in x
                                  and engine_results.remove(x) is None)

            results[engine_name] = engine_results

        # update engine-specific stats
        for engine_name, engine_results in results.items():
            engines[engine_name].stats['search_count'] += 1
            engines[engine_name].stats['result_count'] += len(engine_results)

        # score results and remove duplications
        self.results = score_results(results)

        # merge infoboxes according to their ids
        self.infoboxes = merge_infoboxes(self.infoboxes)

        # update engine stats, using calculated score
        for result in self.results:
            for res_engine in result['engines']:
                engines[result['engine']]\
                    .stats['score_count'] += result['score']

        # return results, suggestions, answers and infoboxes
        return self
