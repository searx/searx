#!/usr/bin/env python
"""
Import searx directly will raise error.
User have to set `SEARX_DEBUG` env or searx's secret key to pass that error

>>> import searx
ERROR:searx:server.secret_key is not changed. Please use something else instead of ultrasecretkey.
NameError: name 'exit' is not defined
>>> from os import environ
... environ.setdefault('SEARX_DEBUG', 'true')
... import searx

Getting categories without initiate the engine will only return `['general']`

>>> import searx.engines
... list(searx.engines.categories.keys())
['general']
>>> from searx import settings
... searx.engines.initialize_engines(searx.settings['engines'])
... list(searx.engines.categories.keys())
['general', 'it', 'science', 'images', 'news', 'videos', 'music', 'files', 'social media', 'map']
"""

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

(C) 2016- by Alexandre Flament, <alex@al-f.net>
'''

# set path
#  from sys import path
#  from os.path import realpath, dirname
#  path.append(realpath(dirname(realpath(__file__)) + '/../'))

# initialization
from json import dumps
from typing import Any, Dict, List, Optional, Tuple, Union
import argparse
import codecs
import sys

from searx import settings

import searx.query
import searx.search
import searx.engines
import searx.preferences


if sys.version_info[0] == 3:
    PY3 = True
else:
    PY3 = False


def get_search_query(args, engines=settings['engines']):
    # type: (argparse.Namespace, Union[List[Any], None]) -> searx.query.SearchQuery
    # search results for the query
    try:
        category = args.category.decode('utf-8')
    except AttributeError:
        category = args.category
    form = {
        "q": args.query,
        "categories": category,
        "pageno": str(args.pageno),
        "language": args.lang,
        "time_range": args.timerange
    }
    if PY3:
        preferences = searx.preferences.Preferences(
            ['oscar'], list(searx.engines.categories.keys()), searx.engines.engines, [])
    else:
        preferences = searx.preferences.Preferences(
            ['oscar'], searx.engines.categories.keys(), searx.engines.engines, [])
    preferences.key_value_settings['safesearch'].parse(args.safesearch)

    search_query, raw_text_query = searx.search.get_search_query_from_webapp(preferences, form)
    # deduplicate engines
    new_sq_engines = []  # type: List[Dict[str, Any]]
    sq_engines = search_query.engines
    for item in sq_engines:
        if item not in new_sq_engines:
            new_sq_engines.append(item)
    search_query.engines = new_sq_engines
    return search_query


def get_result(args=None, engines=settings['engines'], search_query=None):
    # type: (argparse.Namespace, Union[List[Any], None], Union[searx.query.SearchQuery, None]) -> Tuple[searx.query.SearchQuery, searx.results.ResultContainer]  # NOQA
    if args is None and search_query is None:
        raise ValueError('args or search_query parameter required')
    if search_query is None:
        search_query = get_search_query(args, engines)  # type: ignore
    search = searx.search.Search(search_query)
    result_container = search.search()
    return search_query, result_container


def main(args, engines=settings['engines']):
    # type: (argparse.Namespace, Union[List[Any], None]) -> str
    search_query, result_container = get_result(args, engines)

    # output
    from datetime import datetime

    def no_parsed_url(results):
        for result in results:
            del result['parsed_url']
        return results

    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial
        if isinstance(obj, bytes):
            return obj.decode('utf8')
        if isinstance(obj, set):
            return list(obj)
        raise TypeError("Type ({}) not serializable".format(type(obj)))

    result_container_json = {
        "search": {
            "q": search_query.query,
            "pageno": search_query.pageno,
            "lang": search_query.lang,
            "safesearch": search_query.safesearch,
            "timerange": search_query.time_range,
            "engines": search_query.engines
        },
        "results": no_parsed_url(result_container.get_ordered_results()),
        "infoboxes": result_container.infoboxes,
        "suggestions": list(result_container.suggestions),
        "answers": list(result_container.answers),
        "paging": result_container.paging,
        "results_number": result_container.results_number()
    }
    kwargs = dict(sort_keys=True, indent=4, ensure_ascii=False, encoding="utf-8", default=json_serial)
    if PY3:
        kwargs.pop('encoding')
    dump_result = dumps(result_container_json, **kwargs)  # type: ignore
    return dump_result


def parse_argument(
        args: Optional[List[str]]=None,
        category_choices: Optional[List[str]]=None
) -> argparse.Namespace:
    """Parse command line.

    raise SystemExit if not query argument on `args`

    Examples:

    >>> from os import environ
    ... environ.setdefault('SEARX_DEBUG', 'true')
    ... searx.engines.initialize_engines(settings['engines'])
    ... parse_argument()
    standalone_searx.py: error: the following arguments are required: query
    *** SystemExit: 2
    >>> parse_argument(['rain'])
    Namespace(category='general', lang='all', pageno=1, query='rain', safesearch='0', timerange=None)
    """
    if not category_choices:
        category_choices = list(searx.engines.categories.keys())
    parser = argparse.ArgumentParser(description='Standalone searx.')
    parser.add_argument('query', type=str,
                        help='Text query')
    parser.add_argument('--category', type=str, nargs='?',
                        choices=category_choices,
                        default='general',
                        help='Search category')
    parser.add_argument('--lang', type=str, nargs='?', default='all',
                        help='Search language')
    parser.add_argument('--pageno', type=int, nargs='?', default=1,
                        help='Page number starting from 1')
    parser.add_argument('--safesearch', type=str, nargs='?', choices=['0', '1', '2'], default='0',
                        help='Safe content filter from none to strict')
    parser.add_argument('--timerange', type=str, nargs='?', choices=['day', 'week', 'month', 'year'],
                        help='Filter by time range')
    parsed_args = parser.parse_args(args)
    return parsed_args


if __name__ == '__main__':
    from os import environ
    environ.setdefault('SEARX_DEBUG', 'true')
    searx.engines.initialize_engines(settings['engines'])
    args = parse_argument(sys.argv[1:])
    if args:
        res = main(args, None)
        if PY3:
            sys.stdout.write(res)
        else:
            sys.stdout = codecs.getwriter("UTF-8")(sys.stdout)  # type: ignore
            sys.stdout.write(res)
