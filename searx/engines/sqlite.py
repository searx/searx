# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 SQLite database (Offline)
"""

# pylint: disable=missing-function-docstring

import sqlite3

engine_type = 'offline'
database = ""
query_str = ""
limit = 10
paging = True
result_template = 'key-value.html'


def init(engine_settings):
    if 'query_str' not in engine_settings:
        raise ValueError('query_str cannot be empty')

    if not engine_settings['query_str'].lower().startswith('select '):
        raise ValueError('only SELECT query is supported')


def search(query, params):
    query_params = {'query': query}
    query_to_run = query_str + ' LIMIT {0} OFFSET {1}'.format(limit, (params['pageno'] - 1) * limit)

    connection = sqlite3.connect(database)
    cur = connection.cursor()
    cur.execute(query_to_run, query_params)
    results = _fetch_results(cur)
    cur.close()
    connection.close()

    return results


def _fetch_results(cur):
    results = []
    titles = [name for (name, _, _, _, _, _, _) in cur.description]

    res = cur.fetchone()
    while res:
        result = dict(zip(titles, map(str, res)))
        result['template'] = result_template
        results.append(result)
        res = cur.fetchone()

    return results
