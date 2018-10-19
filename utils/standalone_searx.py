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

(C) 2016- by Alexandre Flament, <alex@al-f.net>
'''

# set path
from sys import path
from os.path import realpath, dirname
path.append(realpath(dirname(realpath(__file__)) + '/../'))

# initialization
from json import dumps
from searx import settings
import sys
import codecs
import searx.query
import searx.search
import searx.engines
import searx.preferences
import argparse

searx.engines.initialize_engines(settings['engines'])

# command line parsing
parser = argparse.ArgumentParser(description='Standalone searx.')
parser.add_argument('query', type=str,
                    help='Text query')
parser.add_argument('--category', type=str, nargs='?',
                    choices=searx.engines.categories.keys(),
                    default='general',
                    help='Search category')
parser.add_argument('--lang', type=str, nargs='?',default='all',
                    help='Search language')
parser.add_argument('--pageno', type=int, nargs='?', default=1,
                    help='Page number starting from 1')
parser.add_argument('--safesearch', type=str, nargs='?', choices=['0', '1', '2'], default='0',
                    help='Safe content filter from none to strict')
parser.add_argument('--timerange', type=str, nargs='?', choices=['day', 'week', 'month', 'year'],
                    help='Filter by time range')
args = parser.parse_args()

# search results for the query
form = {
    "q":args.query,
    "categories":args.category.decode('utf-8'),
    "pageno":str(args.pageno),
    "language":args.lang,
    "time_range":args.timerange
}
preferences = searx.preferences.Preferences(['oscar'], searx.engines.categories.keys(), searx.engines.engines, [])
preferences.key_value_settings['safesearch'].parse(args.safesearch)

search_query = searx.search.get_search_query_from_webapp(preferences, form)
search = searx.search.Search(search_query)
result_container = search.search()

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
    raise TypeError ("Type not serializable")

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
sys.stdout = codecs.getwriter("UTF-8")(sys.stdout)
sys.stdout.write(dumps(result_container_json, sort_keys=True, indent=4, ensure_ascii=False, encoding="utf-8", default=json_serial))

