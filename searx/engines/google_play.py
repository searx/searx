"""
 Google Play

 @website     https://play.google.com/store
 @provide-api no

 @using-api   no
 @results     HTML
 @stable      yes
 @parse       url, title, content, img_src
"""

from lxml import html
from searx.engines.xpath import extract_text

# engine dependent config
paging = False
base_url = 'https://play.google.com'

# specific xpath variables
result_xpath = '//div[@class="WHE7ib mpg5gc"]'
title_xpath = './/div[@class="RZEgze"]//div[@title and not(@title="")]/a'
url_xpath = './/div[@class="RZEgze"]//div[@title and not(@title="")]/a/@href'
content_xpath = './/div[@class="RZEgze"]//a[@class="mnKHRc"]'
thumbnail_xpath = './/div[@class="uzcko"]//img/@data-src'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=query)

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(result_xpath):
        title = extract_text(result.xpath(title_xpath))
        url = base_url + result.xpath(url_xpath)[0]
        content = extract_text(result.xpath(content_xpath))
        thumbnail = result.xpath(thumbnail_xpath)[0]

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'img_src': thumbnail})

    return results
