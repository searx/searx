"""
 ScanR Structures (Science)

 @website     https://scanr.enseignementsup-recherche.gouv.fr
 @provide-api yes (https://scanr.enseignementsup-recherche.gouv.fr/api/swagger-ui.html)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content, img_src
"""

from json import loads, dumps
from searx.utils import html_to_text

# engine dependent config
categories = ['science']
paging = True
page_size = 20

# search-url
url = 'https://scanr.enseignementsup-recherche.gouv.fr/'
search_url = url + 'api/structures/search'


# do search-request
def request(query, params):

    params['url'] = search_url
    params['method'] = 'POST'
    params['headers']['Content-type'] = "application/json"
    params['data'] = dumps({"query": query,
                            "searchField": "ALL",
                            "sortDirection": "ASC",
                            "sortOrder": "RELEVANCY",
                            "page": params['pageno'],
                            "pageSize": page_size})

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # return empty array if there are no results
    if search_res.get('total', 0) < 1:
        return []

    # parse results
    for result in search_res['results']:
        if 'id' not in result:
            continue

        # is it thumbnail or img_src??
        thumbnail = None
        if 'logo' in result:
            thumbnail = result['logo']
            if thumbnail[0] == '/':
                thumbnail = url + thumbnail

        content = None
        if 'highlights' in result:
            content = result['highlights'][0]['value']

        # append result
        results.append({'url': url + 'structure/' + result['id'],
                        'title': result['label'],
                        # 'thumbnail': thumbnail,
                        'img_src': thumbnail,
                        'content': html_to_text(content)})

    # return results
    return results
