# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 MongoDB engine (Offline)
"""

# pylint: disable=missing-function-docstring
# pylint: disable=import-error

import re
from pymongo import MongoClient

engine_type = 'offline'
paging = True
# mongodb connection variables
host = '127.0.0.1'
port = 27017
username = ''
password = ''
database = None
collection = None
key = None
# engine specific variables
results_per_page = 20
exact_match_only = False
result_template = 'key-value.html'

_client = None


def init(_):
    connect()


def connect():
    global _client
    kwargs = {
        'port': port,
    }
    if username:
        kwargs['username'] = username
    if password:
        kwargs['password'] = password
    _client = MongoClient(host, **kwargs)[database][collection]


def search(query, params):
    ret = []
    if exact_match_only:
        q = {'$eq': query}
    else:
        q = {'$regex': re.compile('.*{0}.*'.format(re.escape(query)), re.I | re.M)}
    results = _client.find({key: q})\
        .skip((params['pageno'] - 1) * results_per_page)\
        .limit(results_per_page)
    ret.append({'number_of_results': results.count()})
    for r in results:
        del(r['_id'])
        r = {str(k): str(v) for k, v in r.items()}
        r['template'] = result_template
        ret.append(r)
    return ret
