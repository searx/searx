# Invidious (Videos)
#
# @website     https://invidio.us/
# @provide-api yes (https://github.com/omarroth/invidious/wiki/API)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, content, publishedDate, thumbnail, embedded

from json import loads
from searx.url_utils import quote_plus

# engine dependent config
categories = ["videos", "music"]
paging = False
language_support = False
time_range_support = False

base_url = "https://invidio.us/"

# do search-request
def request(query, params):
    search_url = base_url + "api/v1/search?q={query}"
    params["url"] = search_url.format(query=quote_plus(query))
    return params


# get response from search-request
def response(resp):
    results = []

    search_results = loads(resp.text)
    embedded_url = (
        '<iframe width="540" height="304" '
        + 'data-src="'
        + base_url
        + 'embed/{videoid}" '
        + 'frameborder="0" allowfullscreen></iframe>'
    )

    base_invidious_url = base_url + "watch?v="

    for result in search_results:
        rtype = result.get("type", None)
        if rtype == "video":
            videoid = result.get("videoId", None)
            if not videoid:
                continue

            url = base_invidious_url + videoid
            embedded = embedded_url.format(videoid=videoid)
            thumbs = result.get("videoThumbnails", [])
            thumb = next(
                (th for th in thumbs if th["quality"] == "sddefault"), None
            )
            if thumb:
                thumbnail = thumb.get("url", "")
            else:
                thumbnail = ""

            results.append(
                {
                    "url": url,
                    "title": result.get("title", ""),
                    "content": result.get("description", ""),
                    "template": "videos.html",
                    "embedded": embedded,
                    "thumbnail": thumbnail,
                }
            )

    return results
