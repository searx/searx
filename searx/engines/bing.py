"""
 Bing (Web)

 @website     https://www.bing.com
 @provide-api yes (http://datamarket.azure.com/dataset/bing/search),
              max. 5000 query/month

 @using-api   no (because of query limit)
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content

 @todo        publishedDate
"""

from urllib import urlencode
from lxml import html
from searx.engines.xpath import extract_text

# engine dependent config
categories = ['general']
paging = True
language_support = True

# search-url
base_url = 'https://www.bing.com/'
search_string = 'search?{query}&first={offset}'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10 + 1

    if params['language'] != 'all':
        query = u'language:{} {}'.format(params['language'].split('-')[0].upper(),
                                         query.decode('utf-8')).encode('utf-8')

    search_path = search_string.format(
        query=urlencode({'q': query}),
        offset=offset)

    params['url'] = base_url + search_path
    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    try:
        results.append({'number_of_results': int(dom.xpath('//span[@class="sb_count"]/text()')[0]
                                                 .split()[0].replace(',', ''))})
    except:
        pass

    # parse results
    for result in dom.xpath('//div[@class="sa_cc"]'):
        link = result.xpath('.//h3/a')[0]
        url = link.attrib.get('href')
        title = extract_text(link)
        content = extract_text(result.xpath('.//p'))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # parse results again if nothing is found yet
    for result in dom.xpath('//li[@class="b_algo"]'):
        link = result.xpath('.//h2/a')[0]
        url = link.attrib.get('href')
        title = extract_text(link)
        content = extract_text(result.xpath('.//p'))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # return results
    return results
