"""
 peertube (Videos)

 @website     https://www.peertube.live
 @provide-api yes (https://docs.joinpeertube.org/api-rest-reference.html)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, thumbnail, publishedDate, embedded

 @todo        support languages
"""

from json import loads
from datetime import datetime
from searx.url_utils import urlencode
from searx.utils import html_to_text

# engine dependent config
categories = ["videos"]
paging = True
language_support = True
base_url = "https://peertube.live/"


# do search-request
def request(query, params):
    print(params)
    pageno = (params["pageno"] - 1) * 15
    search_url = base_url + "api/v1/search/videos/?pageno={pageno}&{query}"
    params["url"] = search_url.format(query=urlencode({"search": query}), pageno=pageno)
    return params


def _get_offset_from_pageno(pageno):
    return (pageno - 1) * 15 + 1


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    embedded_url = (
        '<iframe width="560" height="315" sandbox="allow-same-origin allow-scripts allow-popups" '
        + 'src="'
        + base_url
        + '{embed_path}" frameborder="0" allowfullscreen></iframe>'
    )
    # return empty array if there are no results
    if "data" not in search_res:
        return []

    # parse results
    for res in search_res["data"]:
        title = res["name"]
        url = base_url + "/videos/watch/" + res["uuid"]
        description = res["description"]
        if description:
            content = html_to_text(res["description"])
        else:
            content = None
        thumbnail = base_url + res["thumbnailPath"]
        publishedDate = datetime.strptime(res["publishedAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        embedded = embedded_url.format(embed_path=res["embedPath"][1:])

        results.append(
            {
                "template": "videos.html",
                "url": url,
                "title": title,
                "content": content,
                "publishedDate": publishedDate,
                "embedded": embedded,
                "thumbnail": thumbnail,
            }
        )

    # return results
    return results
