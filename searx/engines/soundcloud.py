"""
 Soundcloud (Music)

 @website     https://soundcloud.com
 @provide-api yes (https://developers.soundcloud.com/)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content, publishedDate, embedded
"""

import re
from json import loads
from lxml import html
from dateutil import parser
from searx import logger
from searx.poolrequests import get as http_get
from searx.url_utils import quote_plus, urlencode

try:
    from cStringIO import StringIO
except:
    from io import StringIO

# engine dependent config
categories = ['music']
paging = True

# search-url
url = 'https://api.soundcloud.com/'
search_url = url + 'search?{query}'\
                         '&facet=model'\
                         '&limit=20'\
                         '&offset={offset}'\
                         '&linked_partitioning=1'\
                         '&client_id={client_id}'   # noqa

embedded_url = '<iframe width="100%" height="166" ' +\
    'scrolling="no" frameborder="no" ' +\
    'data-src="https://w.soundcloud.com/player/?url={uri}"></iframe>'

cid_re = re.compile(r'client_id:"([^"]*)"', re.I | re.U)
guest_client_id = ''


def get_client_id():
    response = http_get("https://soundcloud.com")

    if response.ok:
        tree = html.fromstring(response.content)
        script_tags = tree.xpath("//script[contains(@src, '/assets/app')]")
        app_js_urls = [script_tag.get('src') for script_tag in script_tags if script_tag is not None]

        # extracts valid app_js urls from soundcloud.com content
        for app_js_url in app_js_urls:
            # gets app_js and searches for the clientid
            response = http_get(app_js_url)
            if response.ok:
                cids = cid_re.search(response.text)
                if cids is not None and len(cids.groups()):
                    return cids.groups()[0]
    logger.warning("Unable to fetch guest client_id from SoundCloud, check parser!")
    return ""


def init():
    global guest_client_id
    # api-key
    guest_client_id = get_client_id()


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 20

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      offset=offset,
                                      client_id=guest_client_id)

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # parse results
    for result in search_res.get('collection', []):
        if result['kind'] in ('track', 'playlist'):
            title = result['title']
            content = result['description']
            publishedDate = parser.parse(result['last_modified'])
            uri = quote_plus(result['uri'])
            embedded = embedded_url.format(uri=uri)

            # append result
            results.append({'url': result['permalink_url'],
                            'title': title,
                            'publishedDate': publishedDate,
                            'embedded': embedded,
                            'content': content})

    # return results
    return results
