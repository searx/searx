# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 peertube (Videos)
"""

from json import loads
from datetime import datetime
from urllib.parse import urlencode
from searx.utils import html_to_text

# about
about = {
    "website": 'https://joinpeertube.org',
    "wikidata_id": 'Q50938515',
    "official_api_documentation": 'https://docs.joinpeertube.org/api-rest-reference.html',
    "use_official_api": True,
    "require_api_key": False,
    "results": 'JSON',
}

# engine dependent config
categories = ["videos"]
paging = True
base_url = "https://peer.tube/"
supported_languages_url = base_url + "api/v1/videos/languages"


# do search-request
def request(query, params):
    pageno = (params["pageno"] - 1) * 15
    search_url = base_url + "api/v1/search/videos/?pageno={pageno}&{query}"
    query_dict = {"search": query}
    language = params["language"].split("-")[0]
    # pylint: disable=undefined-variable
    if "all" != language and language in supported_languages:
        query_dict["languageOneOf"] = language
    params["url"] = search_url.format(
        query=urlencode(query_dict), pageno=pageno
    )
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


def _fetch_supported_languages(resp):
    peertube_languages = list(loads(resp.text).keys())
    return peertube_languages
