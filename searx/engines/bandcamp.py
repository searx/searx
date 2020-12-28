"""
Bandcamp (Music)

@website     https://bandcamp.com/
@provide-api no
@results     HTML
@parse       url, title, content, publishedDate, embedded
"""

from urllib.parse import urlencode, urlparse, parse_qs
from searx.utils import extract_text
from dateutil.parser import parse as dateparse
from lxml import html

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
    search_results = tree.xpath('//li[contains(@class, "searchresult")]')
    for result in search_results:
       
        link = result.xpath('//div[@class="itemurl"]/a')
        result_id = parse_qs(urlparse(link.get('href')).query)["search_item_id"][0]
        title = result.xpath('//div[@class="heading"]/a/text()')[0]
        date = dateparse(result.xpath('//div[@class="released"]/text()')[0].replace("released ", ""))
        content = result.xpath('//div[@class="subhead"]/text()')[0]
        new_result = {'url': extract_text(link), 'title': title, 'content': content, 'publishedDate': date}
        if "album" in result.classes:
            result["embedded"] = album_embedded_url.format(album_id=result_id)
        elif "track" in result.classes:
            result["embedded"] = track_embedded_url.format(album_id=result_id)
        results.append()
    return results
