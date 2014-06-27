from lxml import html


base_url = 'http://www.general-file.com'
search_url = base_url + '/files-{letter}/{query}/{pageno}'

result_xpath = '//table[@class="block-file"]'
title_xpath = './/h2/a//text()'
url_xpath = './/h2/a/@href'
content_xpath = './/p//text()'

paging = True


def request(query, params):
    params['url'] = search_url.format(query=query,
                                      letter=query[0],
                                      pageno=params['pageno'])
    return params


def response(resp):

    results = []
    dom = html.fromstring(resp.text)
    for result in dom.xpath(result_xpath):
        url = result.xpath(url_xpath)[0]
        # skip fast download links
        if not url.startswith('/'):
            continue
        results.append({'url': base_url + url,
                        'title': ''.join(result.xpath(title_xpath)),
                        'content': ''.join(result.xpath(content_xpath))})

    return results
