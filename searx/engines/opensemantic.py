"""
Open Semantic Search

 @website    https://www.opensemanticsearch.org/
 @provide-api yes (https://www.opensemanticsearch.org/dev)

 @using-api  yes
 @results    JSON
 @stable     yes
 @parse      url, title, content, publishedDate
"""
from dateutil import parser
from json import loads
from urllib.parse import quote

base_url = 'http://localhost:8983/solr/opensemanticsearch/'
search_string = 'query?q={query}'


def request(query, params):
    search_path = search_string.format(
        query=quote(query),
    )
    params['url'] = base_url + search_path
    return params


def response(resp):
    results = []
    data = loads(resp.text)
    docs = data.get('response', {}).get('docs', [])

    for current in docs:
        item = {}
        item['url'] = current['id']
        item['title'] = current['title_txt_txt_en']
        if current.get('content_txt'):
            item['content'] = current['content_txt'][0]
        item['publishedDate'] = parser.parse(current['file_modified_dt'])
        results.append(item)

    return results
