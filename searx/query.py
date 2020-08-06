#!/usr/bin/env python

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

(C) 2014 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>
'''

import re

from searx.languages import language_codes
from searx.engines import (
    categories, engines, engine_shortcuts
)


VALID_LANGUAGE_CODE = re.compile(r'^[a-z]{2,3}(-[a-zA-Z]{2})?$')


class RawTextQuery(object):
    """parse raw text query (the value from the html input)"""

    def __init__(self, query, disabled_engines):
        self.query = query
        self.disabled_engines = []

        if disabled_engines:
            self.disabled_engines = disabled_engines

        self.query_parts = []
        self.engines = []
        self.languages = []
        self.timeout_limit = None
        self.external_bang = None
        self.specific = False

    # parse query, if tags are set, which
    # change the search engine or search-language
    def parse_query(self):
        self.query_parts = []

        # split query, including whitespaces
        raw_query_parts = re.split(r'(\s+)' if isinstance(self.query, str) else b'(\s+)', self.query)

        parse_next = True

        for query_part in raw_query_parts:
            if not parse_next:
                self.query_parts[-1] += query_part
                continue

            parse_next = False

            # part does only contain spaces, skip
            if query_part.isspace()\
               or query_part == '':
                parse_next = True
                self.query_parts.append(query_part)
                continue

            # this force the timeout
            if query_part[0] == '<':
                try:
                    raw_timeout_limit = int(query_part[1:])
                    if raw_timeout_limit < 100:
                        # below 100, the unit is the second ( <3 = 3 seconds timeout )
                        self.timeout_limit = float(raw_timeout_limit)
                    else:
                        # 100 or above, the unit is the millisecond ( <850 = 850 milliseconds timeout )
                        self.timeout_limit = raw_timeout_limit / 1000.0
                    parse_next = True
                except ValueError:
                    # error not reported to the user
                    pass

            # this force a language
            if query_part[0] == ':':
                lang = query_part[1:].lower().replace('_', '-')

                # check if any language-code is equal with
                # declared language-codes
                for lc in language_codes:
                    lang_id, lang_name, country, english_name = map(str.lower, lc)

                    # if correct language-code is found
                    # set it as new search-language
                    if (lang == lang_id
                        or lang == lang_name
                        or lang == english_name
                        or lang.replace('-', ' ') == country)\
                       and lang not in self.languages:
                            parse_next = True
                            lang_parts = lang_id.split('-')
                            if len(lang_parts) == 2:
                                self.languages.append(lang_parts[0] + '-' + lang_parts[1].upper())
                            else:
                                self.languages.append(lang_id)
                            # to ensure best match (first match is not necessarily the best one)
                            if lang == lang_id:
                                break

                # user may set a valid, yet not selectable language
                if VALID_LANGUAGE_CODE.match(lang):
                    lang_parts = lang.split('-')
                    if len(lang_parts) > 1:
                        lang = lang_parts[0].lower() + '-' + lang_parts[1].upper()
                    if lang not in self.languages:
                        self.languages.append(lang)
                        parse_next = True

            # external bang
            if query_part[0:2] == "!!":
                self.external_bang = query_part[2:]
                parse_next = True
                continue
            # this force a engine or category
            if query_part[0] == '!' or query_part[0] == '?':
                prefix = query_part[1:].replace('-', ' ').replace('_', ' ')

                # check if prefix is equal with engine shortcut
                if prefix in engine_shortcuts:
                    parse_next = True
                    engine_name = engine_shortcuts[prefix]
                    if engine_name in engines:
                        self.engines.append({'category': 'none',
                                             'name': engine_name,
                                             'from_bang': True})

                # check if prefix is equal with engine name
                elif prefix in engines:
                    parse_next = True
                    self.engines.append({'category': 'none',
                                         'name': prefix,
                                         'from_bang': True})

                # check if prefix is equal with categorie name
                elif prefix in categories:
                    # using all engines for that search, which
                    # are declared under that categorie name
                    parse_next = True
                    self.engines.extend({'category': prefix,
                                         'name': engine.name}
                                        for engine in categories[prefix]
                                        if (engine.name, prefix) not in self.disabled_engines)

            if query_part[0] == '!':
                self.specific = True

            # append query part to query_part list
            self.query_parts.append(query_part)

    def changeSearchQuery(self, search_query):
        if len(self.query_parts):
            self.query_parts[-1] = search_query
        else:
            self.query_parts.append(search_query)
        return self

    def getSearchQuery(self):
        if len(self.query_parts):
            return self.query_parts[-1]
        else:
            return ''

    def getFullQuery(self):
        # get full querry including whitespaces
        return ''.join(self.query_parts)


class SearchQuery(object):
    """container for all the search parameters (query, language, etc...)"""

    def __init__(self, query, engines, categories, lang, safesearch, pageno, time_range,
                 timeout_limit=None, preferences=None, external_bang=None):
        self.query = query.encode()
        self.engines = engines
        self.categories = categories
        self.lang = lang
        self.safesearch = safesearch
        self.pageno = pageno
        self.time_range = None if time_range in ('', 'None', None) else time_range
        self.timeout_limit = timeout_limit
        self.preferences = preferences
        self.external_bang = external_bang

    def __str__(self):
        return str(self.query) + ";" + str(self.engines)
