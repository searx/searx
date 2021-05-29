# SPDX-License-Identifier: AGPL-3.0-or-later

from collections.abc import Iterable
from json import loads
from urllib.parse import urlencode
from searx.utils import to_string

about = {
    "website": "https://hub.docker.com",
    "wikidata_id": "Q100769064",
    "official_api_documentation": "https://docs.docker.com/docker-hub/api/latest/",
    "use_official_api": False,
    "require_api_key": False,
    "results": "JSON",
}

categories = ["it"]
paging = True

search_url = "https://index.docker.io/v1/search?q={query}&page={pageno}"
# url_query = None

# parameters for engines with paging support
#
# number of results on each page
# (only needed if the site requires not a page number, but an offset)
page_size = 25
# number of the first page (usually 0 or 1)
first_page_num = 1


def iterate(iterable):
    if type(iterable) == dict:
        it = iterable.items()

    else:
        it = enumerate(iterable)
    for index, value in it:
        yield str(index), value


def is_iterable(obj):
    if type(obj) == str:
        return False
    return isinstance(obj, Iterable)


def parse(query):
    q = []
    for part in query.split("/"):
        if part == "":
            continue
        else:
            q.append(part)
    return q


def do_query(data, q):
    ret = []
    if not q:
        return ret

    qkey = q[0]

    for key, value in iterate(data):

        if len(q) == 1:
            if key == qkey:
                ret.append(value)
            elif is_iterable(value):
                ret.extend(do_query(value, q))
        else:
            if not is_iterable(value):
                continue
            if key == qkey:
                ret.extend(do_query(value, q[1:]))
            else:
                ret.extend(do_query(value, q))
    return ret


def query(data, query_string):
    q = parse(query_string)

    return do_query(data, q)


def request(query, params):
    query = urlencode({"q": query})[2:]

    fp = {"query": query}
    if search_url.find("{pageno}") >= 0:
        fp["pageno"] = (params["pageno"] - 1) * page_size + first_page_num

    params["url"] = search_url.format(**fp)
    params["query"] = query

    return params


def response(resp):
    results = []
    json = loads(resp.text)

    rs = query(json, "results")
    if not len(rs):
        return results
    for result in rs[0]:
        try:
            title = query(result, "name")[0]
        except:
            continue

        if "/" in title:
            url = "https://hub.docker.com/r/" + title
        else:
            url = "https://hub.docker.com/_/" + title

        try:
            content = query(result, "description")[0]
        except:
            content = ""
        results.append(
            {
                "url": to_string(url),
                "title": to_string(title),
                "content": to_string(content),
            }
        )

    return results
