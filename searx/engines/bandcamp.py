"""
Bandcamp (Music)

@website     https://bandcamp.com/
@provide-api no
@results     HTML
@parse       url, title, content, publishedDate, thumbnail, embedded
"""

from urllib.parse import urlencode, urlparse, parse_qs
from lxml import html
from searx.utils import eval_xpath, extract_text

categories = ['music']
paging = True

base_url = "https://bandcamp.com/"
search_string = search_string = 'search?{query}&page={page}'
album_embedded_url = '''<iframe width="100%" height="166"
    scrolling="no" frameborder="no"
    data-src="https://bandcamp.com/EmbeddedPlayer/album={album_id}/size=large/bgcol=ffffff/linkcol=0687f5/tracklist=false/artwork=small/transparent=true/"
></iframe>'''
track_embedded_url = '''<iframe width="100%" height="166"
    scrolling="no" frameborder="no"
    data-src="https://bandcamp.com/EmbeddedPlayer/track={track_id}/size=large/bgcol=ffffff/linkcol=0687f5/tracklist=false/artwork=small/transparent=true/"
></iframe>'''


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

    search_path = search_string.format(
        query=urlencode({'q': query}),
        page=params['pageno'])

    params['url'] = base_url + search_path

    return params


def response(resp):
    '''post-response callback
    resp: requests response object
    '''
    results = []
    tree = html.fromstring(resp.text)
    search_results = tree.xpath('//li[contains(concat(" ",normalize-space(@class)," ")," searchresult ")]')
    for result in search_results:
        if "album" in result.classes:
            results.append({'url': '', 'title': '', 'content': ''})
        elif "track" in result.classes:
            results.append({'url': '', 'title': '', 'content': ''})
    return results
