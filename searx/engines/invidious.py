# Invidious (Videos)
#
# @website     https://invidio.us/
# @provide-api yes (https://github.com/omarroth/invidious/wiki/API)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, content, publishedDate, thumbnail, embedded

from searx.url_utils import quote_plus
from dateutil import parser
import time

# engine dependent config
categories = ["videos", "music"]
paging = True
language_support = True
time_range_support = True

# search-url
base_url = "https://invidio.us/"


# do search-request
def request(query, params):
    time_range_dict = {
        "day": "today",
        "week": "week",
        "month": "month",
        "year": "year",
    }
    search_url = base_url + "api/v1/search?q={query}"
    params["url"] = search_url.format(
        query=quote_plus(query)
    ) + "&page={pageno}".format(pageno=params["pageno"])

    if params["time_range"] in time_range_dict:
        params["url"] += "&date={timerange}".format(
            timerange=time_range_dict[params["time_range"]]
        )

    if params["language"] != "all":
        lang = params["language"].split("-")
        if len(lang) == 2:
            params["url"] += "&range={lrange}".format(lrange=lang[1])

    return params


# get response from search-request
def response(resp):
    results = []

    search_results = resp.json()
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

            publishedDate = parser.parse(
                time.ctime(result.get("published", 0))
            )

            results.append(
                {
                    "url": url,
                    "title": result.get("title", ""),
                    "content": result.get("description", ""),
                    "template": "videos.html",
                    "publishedDate": publishedDate,
                    "embedded": embedded,
                    "thumbnail": thumbnail,
                }
            )

    return results
