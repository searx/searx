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

from searx.languages import language_codes
from searx.engines import (
    categories, engines, engine_shortcuts
)
import string
import re


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
        self.specific = False

    # parse query, if tags are set, which
    # change the serch engine or search-language
    def parse_query(self):
        self.query_parts = []

        # split query, including whitespaces
        raw_query_parts = re.split(r'(\s+)', self.query)

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

            # this force a language
            if query_part[0] == ':':
                lang = query_part[1:].lower()

                # check if any language-code is equal with
                # declared language-codes
                for lc in language_codes:
                    lang_id, lang_name, country = map(str.lower, lc)

                    # if correct language-code is found
                    # set it as new search-language
                    if lang == lang_id\
                       or lang_id.startswith(lang)\
                       or lang == lang_name\
                       or lang.replace('_', ' ') == country:
                        parse_next = True
                        self.languages.append(lang)
                        break

            # this force a engine or category
            if query_part[0] == '!' or query_part[0] == '?':
                prefix = query_part[1:].replace('_', ' ')

                # check if prefix is equal with engine shortcut
                if prefix in engine_shortcuts:
                    parse_next = True
                    self.engines.append({'category': 'none',
                                         'name': engine_shortcuts[prefix]})

                # check if prefix is equal with engine name
                elif prefix in engines:
                    parse_next = True
                    self.engines.append({'category': 'none',
                                         'name': prefix})

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

    def getSearchQuery(self):
        if len(self.query_parts):
            return self.query_parts[-1]
        else:
            return ''

    def getFullQuery(self):
        # get full querry including whitespaces
        return string.join(self.query_parts, '')


class SearchQuery(object):
    """container for all the search parameters (query, language, etc...)"""

    def __init__(self, query, engines, categories, lang, safesearch, pageno, time_range):
        self.query = query
        self.engines = engines
        self.categories = categories
        self.lang = lang
        self.safesearch = safesearch
        self.pageno = pageno
        self.time_range = time_range

    def __str__(self):
        return str(self.query) + ";" + str(self.engines)
