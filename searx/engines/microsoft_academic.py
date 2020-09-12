"""
Microsoft Academic (Science)

@website     https://academic.microsoft.com
@provide-api yes
@using-api   no
@results     JSON
@stable      no
@parse       url, title, content
"""

from datetime import datetime
from json import loads
from uuid import uuid4
from urllib.parse import urlencode
from searx.utils import html_to_text

categories = ['images']
paging = True
result_url = 'https://academic.microsoft.com/api/search/GetEntityResults?{query}'


def request(query, params):
    correlation_id = uuid4()
    msacademic = uuid4()
    time_now = datetime.now()

    params['url'] = result_url.format(query=urlencode({'correlationId': correlation_id}))
    params['cookies']['msacademic'] = str(msacademic)
    params['cookies']['ai_user'] = 'vhd0H|{now}'.format(now=str(time_now))
    params['method'] = 'POST'
    params['data'] = {
        'Query': '@{query}@'.format(query=query),
        'Limit': 10,
        'Offset': params['pageno'] - 1,
        'Filters': '',
        'OrderBy': '',
        'SortAscending': False,
    }

    return params


def response(resp):
    results = []
    response_data = loads(resp.text)
    if not response_data:
        return results

    for result in response_data['results']:
        url = _get_url(result)
        title = result['e']['dn']
        content = _get_content(result)
        results.append({
            'url': url,
            'title': html_to_text(title),
            'content': html_to_text(content),
        })

    return results


def _get_url(result):
    if 's' in result['e']:
        return result['e']['s'][0]['u']
    return 'https://academic.microsoft.com/#/detail/{pid}'.format(pid=result['id'])


def _get_content(result):
    if 'd' in result['e']:
        content = result['e']['d']
        if len(content) > 300:
            return content[:300] + '...'
        return content

    return ''
