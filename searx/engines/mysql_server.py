# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 MySQL database (Offline)
"""

# error is ignored because the admin has to
# install it manually to use the engine
# pylint: disable=import-error

import mysql.connector


engine_type = 'offline'
auth_plugin = 'caching_sha2_password'
host = "127.0.0.1"
database = ""
username = ""
password = ""
query_str = ""
limit = 10
paging = True
result_template = 'key-value.html'
_connection = None


def init(engine_settings):
    if 'query_str' not in engine_settings:
        raise ValueError('query_str cannot be empty')

    if not engine_settings['query_str'].lower().startswith('select '):
        raise ValueError('only SELECT query is supported')

    global _connection
    _connection = mysql.connector.connect(
        database=database,
        user=username,
        password=password,
        host=host,
        auth_plugin=auth_plugin,
    )


def search(query, params):
    query_params = {'query': query}
    query_to_run = query_str + ' LIMIT {0} OFFSET {1}'.format(limit, (params['pageno'] - 1) * limit)

    with _connection.cursor() as cur:
        cur.execute(query_to_run, query_params)

        return _fetch_results(cur)


def _fetch_results(cur):
    results = []
    for res in cur:
        result = dict(zip(cur.column_names, map(str, res)))
        result['template'] = result_template
        results.append(result)

    return results
