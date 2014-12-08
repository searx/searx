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

import requests as requests_lib
import threading
import re
from itertools import izip_longest, chain
from datetime import datetime
from operator import itemgetter
from urlparse import urlparse, unquote
from searx.engines import (
    categories, engines
)
from searx.languages import language_codes
from searx.utils import gen_useragent
from searx.query import Query


number_of_searches = 0


def threaded_requests(requests):
    for fn, url, request_args in requests:
        th = threading.Thread(
            target=fn,
            args=(url,),
            kwargs=request_args,
            name='search_request',
        )
        th.start()

    for th in threading.enumerate():
        if th.name == 'search_request':
            th.join()


# get default reqest parameter
def default_request_params():
    return {
        'method': 'GET', 'headers': {}, 'data': {}, 'url': '', 'cookies': {}}


# create a callback wrapper for the search engine results
def make_callback(engine_name,
                  results,
                  suggestions,
                  answers,
                  infoboxes,
                  callback,
                  params):

    # creating a callback wrapper for the search engine results
    def process_callback(response, **kwargs):
        cb_res = []
        response.search_params = params

        # callback
        try:
            search_results = callback(response)
        except Exception, e:
            # increase errors stats
            engines[engine_name].stats['errors'] += 1
            results[engine_name] = cb_res

            # print engine name and specific error message
            print '[E] Error with engine "{0}":\n\t{1}'.format(
                engine_name, str(e))
            return

        # add results
        for result in search_results:
            result['engine'] = engine_name

            # if it is a suggestion, add it to list of suggestions
            if 'suggestion' in result:
                # TODO type checks
                suggestions.add(result['suggestion'])
                continue

            # if it is an answer, add it to list of answers
            if 'answer' in result:
                answers.add(result['answer'])
                continue

            # if it is an infobox, add it to list of infoboxes
            if 'infobox' in result:
                infoboxes.append(result)
                continue

            # append result
            cb_res.append(result)

        results[engine_name] = cb_res

        # update stats with current page-load-time
        engines[engine_name].stats['page_load_time'] += \
            (datetime.now() - params['started']).total_seconds()

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
                    categoryPositions[k]['index'] = v+1

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
            infoboxes_id[infobox_id] = len(results)-1

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
        if request.cookies.get('blocked_engines'):
            self.blocked_engines = request.cookies['blocked_engines'].split(',')  # noqa
        else:
            self.blocked_engines = []

        self.results = []
        self.suggestions = []
        self.answers = []
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
        if self.engines:
            self.categories = list(set(engine['category']
                                       for engine in self.engines))

        # otherwise, using defined categories to
        # calculate which engines should be used
        else:
            # set used categories
            for pd_name, pd in self.request_data.items():
                if pd_name.startswith('category_'):
                    category = pd_name[9:]
                    # if category is not found in list, skip
                    if category not in categories:
                        continue

                    # add category to list
                    self.categories.append(category)

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
                                     'name': x.name}
                                    for x in categories[categ]
                                    if x.name not in self.blocked_engines)

    # do search-request
    def search(self, request):
        global number_of_searches

        # init vars
        requests = []
        results = {}
        suggestions = set()
        answers = set()
        infoboxes = []

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
            request_params['started'] = datetime.now()
            request_params['pageno'] = self.pageno
            request_params['language'] = self.lang

            # update request parameters dependent on
            # search-engine (contained in engines folder)
            request_params = engine.request(self.query.encode('utf-8'),
                                            request_params)

            if request_params['url'] is None:
                # TODO add support of offline engines
                pass

            # create a callback wrapper for the search engine results
            callback = make_callback(
                selected_engine['name'],
                results,
                suggestions,
                answers,
                infoboxes,
                engine.response,
                request_params
            )

            # create dictionary which contain all
            # informations about the request
            request_args = dict(
                headers=request_params['headers'],
                hooks=dict(response=callback),
                cookies=request_params['cookies'],
                timeout=engine.timeout
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
            requests.append((req, request_params['url'], request_args))

        # send all search-request
        threaded_requests(requests)

        # update engine-specific stats
        for engine_name, engine_results in results.items():
            engines[engine_name].stats['search_count'] += 1
            engines[engine_name].stats['result_count'] += len(engine_results)

        # score results and remove duplications
        results = score_results(results)

        # merge infoboxes according to their ids
        infoboxes = merge_infoboxes(infoboxes)

        # update engine stats, using calculated score
        for result in results:
            for res_engine in result['engines']:
                engines[result['engine']]\
                    .stats['score_count'] += result['score']

        # return results, suggestions, answers and infoboxes
        return results, suggestions, answers, infoboxes
