#!/usr/bin/env python

"""
 DICT protocol
 @website     https://tools.ietf.org/html/rfc2229
 @provide-api yes
 @using-api   yes
 @results     DICT
 @stable      yes
 @parse       title, content
"""

from dictionary_client import DictionaryClient

categories = ['general']
paging = False
db = '*'
host = 'localhost'
port = 2628
result_template = 'dict.html'
DICT = True


def request(query, params):
    params['query'] = query
    params['method'] = 'define'
    return params


def response(resp):
    results = []
    if not resp or not resp['content']:
        return results

    for definition in resp['content']:
        results.append({
            'title': resp['databases'][definition['db']],
            'content': definition['definition'],
            'template': 'dict.html'
        })
    return results
