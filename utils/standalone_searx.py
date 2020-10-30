#!/usr/bin/env python
"""Script to run searx from terminal.

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

Example to use this script:

.. code::  bash

    $ export SEARX_DEBUG=1 && python3 utils/standalone_searx.py rain
"""  # noqa: E501
# pylint: disable=pointless-string-statement
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
# pylint: disable=wrong-import-position
import argparse
import sys
from datetime import datetime
from json import dumps
from typing import Any, Dict, List, Optional, Tuple

import searx.engines
import searx.preferences
import searx.query
import searx.search
import searx.webadapter
from searx import settings


def get_search_query(
        args: argparse.Namespace, engine_categories: Optional[List[Any]] = None
) -> searx.search.SearchQuery:
    """Get  search results for the query"""
    if engine_categories is None:
        engine_categories = list(searx.engines.categories.keys())
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
    preferences = searx.preferences.Preferences(
        ['oscar'], engine_categories, searx.engines.engines, [])
    preferences.key_value_settings['safesearch'].parse(args.safesearch)

    search_query = searx.webadapter.get_search_query_from_webapp(
        preferences, form)[0]
    return search_query


def get_result(
        args: Optional[argparse.Namespace]=None,
        search_query=None,
        engine_categories: Optional[List[Any]] = None
) -> Tuple[searx.search.SearchQuery, searx.results.ResultContainer]:
    """Get search query obj and result container."""
    if args is None and search_query is None:
        raise ValueError('args or search_query parameter required')
    if search_query is None and args is not None:
        search_query = get_search_query(
            args, engine_categories=engine_categories)
    search = searx.search.Search(search_query)
    result_container = search.search()
    return search_query, result_container


def no_parsed_url(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove parsed url from dict."""
    for result in results:
        del result['parsed_url']
    return results


def json_serial(obj: Any) -> Any:
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    if isinstance(obj, bytes):
        return obj.decode('utf8')
    if isinstance(obj, set):
        return list(obj)
    raise TypeError("Type ({}) not serializable".format(type(obj)))


def main(args: argparse.Namespace) -> Dict[str, Any]:
    """Get result from parsed arguments."""
    search_query, result_container = get_result(args)
    result_container_json = {
        "search": {
            "q": search_query.query,
            "pageno": search_query.pageno,
            "lang": search_query.lang,
            "safesearch": search_query.safesearch,
            "timerange": search_query.time_range,
        },
        "results": no_parsed_url(result_container.get_ordered_results()),
        "infoboxes": result_container.infoboxes,
        "suggestions": list(result_container.suggestions),
        "answers": list(result_container.answers),
        "paging": result_container.paging,
        "results_number": result_container.results_number()
    }
    return result_container_json


def parse_argument(
        args: Optional[List[str]]=None,
        category_choices: Optional[List[str]]=None
) -> argparse.Namespace:
    """Parse command line.

    raise SystemExit if query argument not on `args`

    Examples:

    >>> from os import environ
    ... import searx.engines
    ... environ.setdefault('SEARX_DEBUG', 'true')
    ... searx.engines.initialize_engines(settings['engines'])
    ... parse_argument()
    standalone_searx.py: error: the following arguments are required: query
    *** SystemExit: 2
    >>> parse_argument(['rain'])
    Namespace(category='general', lang='all', pageno=1, query='rain', safesearch='0', timerange=None)
    """  # noqa: E501
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
    parser.add_argument(
        '--safesearch', type=str, nargs='?',
        choices=['0', '1', '2'], default='0',
        help='Safe content filter from none to strict')
    parser.add_argument(
        '--timerange', type=str,
        nargs='?', choices=['day', 'week', 'month', 'year'],
        help='Filter by time range')
    return parser.parse_args(args)


if __name__ == '__main__':
    searx.engines.initialize_engines(settings['engines'])
    prog_args = parse_argument()
    res = main(prog_args)
    sys.stdout.write(dumps(
        res, sort_keys=True, indent=4, ensure_ascii=False,
        efault=json_serial))
