"""
 General Files (Files)

 @website     http://www.general-files.org
 @provide-api no (nothing found)

 @using-api   no (because nothing found)
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content

 @todo        detect torrents?
"""

from lxml import html

# engine dependent config
categories = ['files']
paging = True

# search-url
base_url = 'http://www.general-file.com'
search_url = base_url + '/files-{letter}/{query}/{pageno}'

# specific xpath variables
result_xpath = '//table[@class="block-file"]'
title_xpath = './/h2/a//text()'
url_xpath = './/h2/a/@href'
content_xpath = './/p//text()'


# do search-request
def request(query, params):

    params['url'] = search_url.format(query=query,
                                      letter=query[0],
                                      pageno=params['pageno'])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(result_xpath):
        url = result.xpath(url_xpath)[0]

        # skip fast download links
        if not url.startswith('/'):
            continue

        # append result
        results.append({'url': base_url + url,
                        'title': ''.join(result.xpath(title_xpath)),
                        'content': ''.join(result.xpath(content_xpath))})

    # return results
    return results
