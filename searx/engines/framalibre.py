"""
 FramaLibre (It)

 @website     https://framalibre.org/
 @provide-api no

 @using-api   no
 @results     HTML
 @stable      no (HTML can change)
 @parse       url, title, content, thumbnail, img_src
"""

from cgi import escape
from lxml import html
from searx.engines.xpath import extract_text
from searx.url_utils import urljoin, urlencode

# engine dependent config
categories = ['it']
paging = True

# search-url
base_url = 'https://framalibre.org/'
search_url = base_url + 'recherche-par-crit-res?{query}&page={offset}'

# specific xpath variables
results_xpath = '//div[@class="nodes-list-row"]/div[contains(@typeof,"sioc:Item")]'
link_xpath = './/h3[@class="node-title"]/a[@href]'
thumbnail_xpath = './/img[@class="media-object img-responsive"]/@src'
content_xpath = './/div[@class="content"]//p'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1)
    params['url'] = search_url.format(query=urlencode({'keys': query}),
                                      offset=offset)

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(results_xpath):
        link = result.xpath(link_xpath)[0]
        href = urljoin(base_url, link.attrib.get('href'))
        # there's also a span (class="rdf-meta element-hidden" property="dc:title")'s content property for this...
        title = escape(extract_text(link))
        thumbnail_tags = result.xpath(thumbnail_xpath)
        thumbnail = None
        if len(thumbnail_tags) > 0:
            thumbnail = extract_text(thumbnail_tags[0])
            if thumbnail[0] == '/':
                thumbnail = base_url + thumbnail
        content = escape(extract_text(result.xpath(content_xpath)))

        # append result
        results.append({'url': href,
                        'title': title,
                        'img_src': thumbnail,
                        'content': content})

    # return results
    return results
