from json import loads
from urlparse import urljoin

local_url = None

def request(query, params):
    params['url'] = urljoin(local_url, '/lsearch?q=%s' % query)
    return params


def response(resp):
    results = loads(resp.text)

    return results
