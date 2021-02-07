"""
Docker Hub (IT)

@website     https://hub.docker.com
@provide-api yes (https://docs.docker.com/registry/spec/api/)

@using-api   yes
@results     JSON
@stable      yes
@parse       url, title, content, thumbnail, publishedDate
"""

from json import loads
from dateutil import parser
from urllib.parse import urlencode

categories = ['it']  # optional
paging = True

base_url = "https://hub.docker.com/"
search_url = base_url + "api/content/v1/products/search?{query}&type=image&page_size=25"


def request(query, params):
    '''pre-request callback
    params<dict>:
      method  : POST/GET
      headers : {}
      data    : {} # if method == POST
      url     : ''
      category: 'search category'
      pageno  : 1 # number of the requested page
    '''

    params['url'] = search_url.format(query=urlencode(dict(q=query, page=params["pageno"])))
    params["headers"]["Search-Version"] = "v3"

    return params


def response(resp):
    '''post-response callback
    resp: requests response object
    '''
    results = []
    body = loads(resp.text)

    # Make sure `summaries` isn't `null`
    search_res = body.get("summaries")
    if search_res:
        for item in search_res:
            result = {}

            # Make sure correct URL is set
            filter_type = item.get("filter_type")
            is_official = (filter_type == "store") or (filter_type == "official")

            result["url"] = base_url + f"_/{item.get('slug')}" if is_official else base_url + f"r/{item.get('slug')}"
            result["title"] = item.get("name")
            result["content"] = item.get("short_description")
            result["publishedDate"] = parser.parse(item.get("updated_at") or item.get("created_at"))
            result["thumbnail"] = item["logo_url"].get("large") or item["logo_url"].get("small")

            results.append(result)

    return results
