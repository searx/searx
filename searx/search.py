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


def default_request_params():
    return {
        'method': 'GET', 'headers': {}, 'data': {}, 'url': '', 'cookies': {}}


def make_callback(engine_name, results, suggestions, callback, params):
    # creating a callback wrapper for the search engine results
    def process_callback(response, **kwargs):
        cb_res = []
        response.search_params = params
        engines[engine_name].stats['page_load_time'] += \
            (datetime.now() - params['started']).total_seconds()
        try:
            search_results = callback(response)
        except Exception, e:
            engines[engine_name].stats['errors'] += 1
            results[engine_name] = cb_res
            print '[E] Error with engine "{0}":\n\t{1}'.format(
                engine_name, str(e))
            return
        for result in search_results:
            result['engine'] = engine_name
            if 'suggestion' in result:
                # TODO type checks
                suggestions.add(result['suggestion'])
                continue
            cb_res.append(result)
        results[engine_name] = cb_res
    return process_callback


def score_results(results):
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

        if hasattr(engines[res['engine']], 'weight'):
            weight = float(engines[res['engine']].weight)

        score = int((flat_len - i) / engines_len) * weight + 1
        duplicated = False

        for new_res in results:
            p1 = res['parsed_url'].path[:-1] if res['parsed_url'].path.endswith('/') else res['parsed_url'].path  # noqa
            p2 = new_res['parsed_url'].path[:-1] if new_res['parsed_url'].path.endswith('/') else new_res['parsed_url'].path  # noqa
            if res['host'] == new_res['host'] and\
               unquote(p1) == unquote(p2) and\
               res['parsed_url'].query == new_res['parsed_url'].query and\
               res.get('template') == new_res.get('template'):
                duplicated = new_res
                break
        if duplicated:
            if res.get('content') > duplicated.get('content'):
                duplicated['content'] = res['content']
            duplicated['score'] += score
            duplicated['engines'].append(res['engine'])
            if duplicated['parsed_url'].scheme == 'https':
                continue
            elif res['parsed_url'].scheme == 'https':
                duplicated['url'] = res['parsed_url'].geturl()
                duplicated['parsed_url'] = res['parsed_url']
        else:
            res['score'] = score
            results.append(res)
    return sorted(results, key=itemgetter('score'), reverse=True)


class Search(object):

    """Search information container"""

    def __init__(self, request):
        super(Search, self).__init__()
        self.query = None
        self.engines = []
        self.categories = []
        self.paging = False
        self.pageno = 1
        self.lang = 'all'
        if request.cookies.get('blocked_engines'):
            self.blocked_engines = request.cookies['blocked_engines'].split(',')  # noqa
        else:
            self.blocked_engines = []
        self.results = []
        self.suggestions = []
        self.request_data = {}

        if request.cookies.get('language')\
           and request.cookies['language'] in (x[0] for x in language_codes):
            self.lang = request.cookies['language']

        if request.method == 'POST':
            self.request_data = request.form
        else:
            self.request_data = request.args

        # TODO better exceptions
        if not self.request_data.get('q'):
            raise Exception('noquery')

        self.query = self.request_data['q']

        pageno_param = self.request_data.get('pageno', '1')
        if not pageno_param.isdigit() or int(pageno_param) < 1:
            raise Exception('wrong pagenumber')

        self.pageno = int(pageno_param)

        self.parse_query()

        self.categories = []

        if self.engines:
            self.categories = list(set(engine['category']
                                       for engine in self.engines))
        else:
            for pd_name, pd in self.request_data.items():
                if pd_name.startswith('category_'):
                    category = pd_name[9:]
                    if not category in categories:
                        continue
                    self.categories.append(category)
            if not self.categories:
                cookie_categories = request.cookies.get('categories', '')
                cookie_categories = cookie_categories.split(',')
                for ccateg in cookie_categories:
                    if ccateg in categories:
                        self.categories.append(ccateg)
            if not self.categories:
                self.categories = ['general']

            for categ in self.categories:
                self.engines.extend({'category': categ,
                                     'name': x.name}
                                    for x in categories[categ]
                                    if not x.name in self.blocked_engines)

    def parse_query(self):
        query_parts = self.query.split()
        modified = False
        if query_parts[0].startswith(':'):
            lang = query_parts[0][1:].lower()

            for lc in language_codes:
                lang_id, lang_name, country = map(str.lower, lc)
                if lang == lang_id\
                   or lang_id.startswith(lang)\
                   or lang == lang_name\
                   or lang == country:
                    self.lang = lang
                    modified = True
                    break

        elif query_parts[0].startswith('!'):
            prefix = query_parts[0][1:].replace('_', ' ')

            if prefix in engine_shortcuts\
               and not engine_shortcuts[prefix] in self.blocked_engines:
                modified = True
                self.engines.append({'category': 'none',
                                     'name': engine_shortcuts[prefix]})
            elif prefix in engines\
                    and not prefix in self.blocked_engines:
                modified = True
                self.engines.append({'category': 'none',
                                    'name': prefix})
            elif prefix in categories:
                modified = True
                self.engines.extend({'category': prefix,
                                    'name': engine.name}
                                    for engine in categories[prefix]
                                    if not engine in self.blocked_engines)
        if modified:
            self.query = self.query.replace(query_parts[0], '', 1).strip()
            self.parse_query()

    def search(self, request):
        global number_of_searches
        requests = []
        results = {}
        suggestions = set()
        number_of_searches += 1
        #user_agent = request.headers.get('User-Agent', '')
        user_agent = gen_useragent()

        for selected_engine in self.engines:
            if selected_engine['name'] not in engines:
                continue

            engine = engines[selected_engine['name']]

            if self.pageno > 1 and not engine.paging:
                continue

            if self.lang != 'all' and not engine.language_support:
                continue

            request_params = default_request_params()
            request_params['headers']['User-Agent'] = user_agent
            request_params['category'] = selected_engine['category']
            request_params['started'] = datetime.now()
            request_params['pageno'] = self.pageno
            request_params['language'] = self.lang
            request_params = engine.request(self.query.encode('utf-8'),
                                            request_params)

            if request_params['url'] is None:
                # TODO add support of offline engines
                pass

            callback = make_callback(
                selected_engine['name'],
                results,
                suggestions,
                engine.response,
                request_params
            )

            request_args = dict(
                headers=request_params['headers'],
                hooks=dict(response=callback),
                cookies=request_params['cookies'],
                timeout=engine.timeout
            )

            if request_params['method'] == 'GET':
                req = grequests.get
            else:
                req = grequests.post
                request_args['data'] = request_params['data']

            # ignoring empty urls
            if not request_params['url']:
                continue

            requests.append(req(request_params['url'], **request_args))
        grequests.map(requests)
        for engine_name, engine_results in results.items():
            engines[engine_name].stats['search_count'] += 1
            engines[engine_name].stats['result_count'] += len(engine_results)

        results = score_results(results)

        for result in results:
            for res_engine in result['engines']:
                engines[result['engine']]\
                    .stats['score_count'] += result['score']

        return results, suggestions
