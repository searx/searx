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

import grequests
from itertools import izip_longest, chain
from datetime import datetime
from operator import itemgetter
from urlparse import urlparse, unquote
from searx.engines import (
    categories, engines, engine_shortcuts
)
from searx.languages import language_codes
from searx.utils import gen_useragent


number_of_searches = 0


# get default reqest parameter
def default_request_params():
    return {
        'method': 'GET', 'headers': {}, 'data': {}, 'url': '', 'cookies': {}}


# create a callback wrapper for the search engine results
def make_callback(engine_name, results, suggestions, callback, params):

    # creating a callback wrapper for the search engine results
    def process_callback(response, **kwargs):
        cb_res = []
        response.search_params = params

        # update stats with current page-load-time
        engines[engine_name].stats['page_load_time'] += \
            (datetime.now() - params['started']).total_seconds()

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
            
        for result in search_results:
            result['engine'] = engine_name

            # if it is a suggestion, add it to list of suggestions
            if 'suggestion' in result:
                # TODO type checks
                suggestions.add(result['suggestion'])
                continue

            # append result
            cb_res.append(result)

        results[engine_name] = cb_res

    return process_callback


# score results and remove duplications
def score_results(results):
    # calculate scoring parameters
    flat_res = filter(
        None, chain.from_iterable(izip_longest(*results.values())))
    flat_len = len(flat_res)
    engines_len = len(results)

    results = []

    # deduplication + scoring
    for i, res in enumerate(flat_res):

        res['parsed_url'] = urlparse(res['url'])

        res['host'] = res['parsed_url'].netloc

        if res['host'].startswith('www.'):
            res['host'] = res['host'].replace('www.', '', 1)

        res['engines'] = [res['engine']]
        weight = 1.0

        # get weight of this engine if possible
        if hasattr(engines[res['engine']], 'weight'):
            weight = float(engines[res['engine']].weight)

        # calculate score for that engine
        score = int((flat_len - i) / engines_len) * weight + 1

        duplicated = False

        # check for duplicates
        for new_res in results:
            # remove / from the end of the url if required
            p1 = res['parsed_url'].path[:-1] if res['parsed_url'].path.endswith('/') else res['parsed_url'].path  # noqa
            p2 = new_res['parsed_url'].path[:-1] if new_res['parsed_url'].path.endswith('/') else new_res['parsed_url'].path  # noqa

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
            if res.get('content') > duplicated.get('content'):
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

    # return results sorted by score
    return sorted(results, key=itemgetter('score'), reverse=True)


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

        # set query
        self.query = self.request_data['q']

        # set pagenumber
        pageno_param = self.request_data.get('pageno', '1')
        if not pageno_param.isdigit() or int(pageno_param) < 1:
            raise Exception('wrong pagenumber')

        self.pageno = int(pageno_param)

        # parse query, if tags are set, which change the serch engine or search-language
        self.parse_query()

        self.categories = []

        # if engines are calculated from query, set categories by using that informations
        if self.engines:
            self.categories = list(set(engine['category']
                                       for engine in self.engines))

        # otherwise, using defined categories to calculate which engines should be used
        else:
            # set used categories
            for pd_name, pd in self.request_data.items():
                if pd_name.startswith('category_'):
                    category = pd_name[9:]
                    # if category is not found in list, skip
                    if not category in categories:
                        continue

                    # add category to list
                    self.categories.append(category)

            # if no category is specified for this search, using user-defined default-configuration which (is stored in cookie)
            if not self.categories:
                cookie_categories = request.cookies.get('categories', '')
                cookie_categories = cookie_categories.split(',')
                for ccateg in cookie_categories:
                    if ccateg in categories:
                        self.categories.append(ccateg)

            # if still no category is specified, using general as default-category
            if not self.categories:
                self.categories = ['general']

            # using all engines for that search, which are declared under the specific categories
            for categ in self.categories:
                self.engines.extend({'category': categ,
                                     'name': x.name}
                                    for x in categories[categ]
                                    if not x.name in self.blocked_engines)

    # parse query, if tags are set, which change the serch engine or search-language
    def parse_query(self):
        query_parts = self.query.split()
        modified = False

        # check if language-prefix is set
        if query_parts[0].startswith(':'):
            lang = query_parts[0][1:].lower()

            # check if any language-code equal with declared language-codes
            for lc in language_codes:
                lang_id, lang_name, country = map(str.lower, lc)

                # if correct language-code is found, set it as new search-language
                if lang == lang_id\
                   or lang_id.startswith(lang)\
                   or lang == lang_name\
                   or lang == country:
                    self.lang = lang
                    modified = True
                    break

        # check if category/engine prefix is set
        elif query_parts[0].startswith('!'):
            prefix = query_parts[0][1:].replace('_', ' ')

            # check if prefix equal with engine shortcut
            if prefix in engine_shortcuts\
               and not engine_shortcuts[prefix] in self.blocked_engines:
                modified = True
                self.engines.append({'category': 'none',
                                     'name': engine_shortcuts[prefix]})

            # check if prefix equal with engine name
            elif prefix in engines\
                    and not prefix in self.blocked_engines:
                modified = True
                self.engines.append({'category': 'none',
                                    'name': prefix})

            # check if prefix equal with categorie name
            elif prefix in categories:
                modified = True
                # using all engines for that search, which are declared under that categorie name
                self.engines.extend({'category': prefix,
                                    'name': engine.name}
                                    for engine in categories[prefix]
                                    if not engine in self.blocked_engines)

        # if language, category or engine were specificed in this query, search for more tags which does the same
        if modified:
            self.query = self.query.replace(query_parts[0], '', 1).strip()
            self.parse_query()

    # do search-request
    def search(self, request):
        global number_of_searches

        # init vars
        requests = []
        results = {}
        suggestions = set()

        # increase number of active searches
        number_of_searches += 1

        # set default useragent
        #user_agent = request.headers.get('User-Agent', '')
        user_agent = gen_useragent()

        # start search-reqest for all selected engines
        for selected_engine in self.engines:
            if selected_engine['name'] not in engines:
                continue

            engine = engines[selected_engine['name']]

            # if paging is not supported, skip
            if self.pageno > 1 and not engine.paging:
                continue

            # if search-language is set and engine does not provide language-support, skip
            if self.lang != 'all' and not engine.language_support:
                continue

            # set default request parameters
            request_params = default_request_params()
            request_params['headers']['User-Agent'] = user_agent
            request_params['category'] = selected_engine['category']
            request_params['started'] = datetime.now()
            request_params['pageno'] = self.pageno
            request_params['language'] = self.lang

            # update request parameters dependent on search-engine (contained in engines folder)
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
                engine.response,
                request_params
            )

            # create dictionary which contain all informations about the request
            request_args = dict(
                headers=request_params['headers'],
                hooks=dict(response=callback),
                cookies=request_params['cookies'],
                timeout=engine.timeout
            )

            # specific type of request (GET or POST)
            if request_params['method'] == 'GET':
                req = grequests.get
            else:
                req = grequests.post
                request_args['data'] = request_params['data']

            # ignoring empty urls
            if not request_params['url']:
                continue

            # append request to list
            requests.append(req(request_params['url'], **request_args))

        # send all search-request
        grequests.map(requests)

        # update engine-specific stats
        for engine_name, engine_results in results.items():
            engines[engine_name].stats['search_count'] += 1
            engines[engine_name].stats['result_count'] += len(engine_results)

        # score results and remove duplications
        results = score_results(results)

        # update engine stats, using calculated score
        for result in results:
            for res_engine in result['engines']:
                engines[result['engine']]\
                    .stats['score_count'] += result['score']

        # return results and suggestions
        return results, suggestions
