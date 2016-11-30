#  INA (Videos)
#
# @website     https://www.ina.fr/
# @provide-api no
#
# @using-api   no
# @results     HTML (using search portal)
# @stable      no (HTML can change)
# @parse       url, title, content, publishedDate, thumbnail
#
# @todo        set content-parameter with correct data
# @todo        embedded (needs some md5 from video page)

from json import loads
from lxml import html
from dateutil import parser
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode

try:
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser

# engine dependent config
categories = ['videos']
paging = True
page_size = 48

# search-url
base_url = 'https://www.ina.fr'
search_url = base_url + '/layout/set/ajax/recherche/result?autopromote=&hf={ps}&b={start}&type=Video&r=&{query}'

# specific xpath variables
results_xpath = '//div[contains(@class,"search-results--list")]/div[@class="media"]'
url_xpath = './/a/@href'
title_xpath = './/h3[@class="h3--title media-heading"]'
thumbnail_xpath = './/img/@src'
publishedDate_xpath = './/span[@class="broadcast"]'
content_xpath = './/p[@class="media-body__summary"]'


# do search-request
def request(query, params):
    params['url'] = search_url.format(ps=page_size,
                                      start=params['pageno'] * page_size,
                                      query=urlencode({'q': query}))

    return params


# get response from search-request
def response(resp):
    results = []

    # we get html in a JSON container...
    response = loads(resp.text)
    if "content" not in response:
        return []
    dom = html.fromstring(response["content"])
    p = HTMLParser()

    # parse results
    for result in dom.xpath(results_xpath):
        videoid = result.xpath(url_xpath)[0]
        url = base_url + videoid
        title = p.unescape(extract_text(result.xpath(title_xpath)))
        thumbnail = extract_text(result.xpath(thumbnail_xpath)[0])
        if thumbnail[0] == '/':
            thumbnail = base_url + thumbnail
        d = extract_text(result.xpath(publishedDate_xpath)[0])
        d = d.split('/')
        # force ISO date to avoid wrong parsing
        d = "%s-%s-%s" % (d[2], d[1], d[0])
        publishedDate = parser.parse(d)
        content = extract_text(result.xpath(content_xpath))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'template': 'videos.html',
                        'publishedDate': publishedDate,
                        'thumbnail': thumbnail})

    # return results
    return results
