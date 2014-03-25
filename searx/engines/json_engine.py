from urllib import urlencode
from json import loads
from collections import Iterable

search_url = None
url_query = None
content_query = None
title_query = None
#suggestion_xpath = ''


def iterate(iterable):
    if type(iterable) == dict:
        it = iterable.iteritems()

    else:
        it = enumerate(iterable)
    for index, value in it:
        yield str(index), value


def is_iterable(obj):
    if type(obj) == str:
        return False
    if type(obj) == unicode:
        return False
    return isinstance(obj, Iterable)


def parse(query):
    q = []
    for part in query.split('/'):
        if part == '':
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
    query = urlencode({'q': query})[2:]
    params['url'] = search_url.format(query=query)
    params['query'] = query
    return params


def response(resp):
    results = []

    json = loads(resp.text)

    urls = query(json, url_query)
    contents = query(json, content_query)
    titles = query(json, title_query)
    for url, title, content in zip(urls, titles, contents):
        results.append({'url': url, 'title': title, 'content': content})
    return results
