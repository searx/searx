from searx.engines import (
    categories, engines, engine_shortcuts
)
from searx.languages import language_codes


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
