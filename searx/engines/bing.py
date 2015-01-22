## Bing (Web)
#
# @website     https://www.bing.com
# @provide-api yes (http://datamarket.azure.com/dataset/bing/search),
#              max. 5000 query/month
#
# @using-api   no (because of query limit)
# @results     HTML (using search portal)
# @stable      no (HTML can change)
# @parse       url, title, content
#
# @todo        publishedDate

from __future__ import absolute_import
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()

from urllib.parse import urlencode
from cgi import escape
from lxml import html

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

    if params['language'] == 'all':
        language = 'en-US'
    else:
        language = params['language'].replace('_', '-')

    search_path = search_string.format(
        query=urlencode({'q': query, 'setmkt': language}),
        offset=offset)

    params['cookies']['SRCHHPGUSR'] = \
        'NEWWND=0&NRSLT=-1&SRCHLANG=' + language.split('-')[0]

    params['url'] = base_url + search_path
    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.content)

    # parse results
    for result in dom.xpath('//div[@class="sa_cc"]'):
        link = result.xpath('.//h3/a')[0]
        url = link.attrib.get('href')
        title = ' '.join(link.xpath('.//text()'))
        content = escape(' '.join(result.xpath('.//p//text()')))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # return results if something is found
    if results:
        return results

    # parse results again if nothing is found yet
    for result in dom.xpath('//li[@class="b_algo"]'):
        link = result.xpath('.//h2/a')[0]
        url = link.attrib.get('href')
        title = ' '.join(link.xpath('.//text()'))
        content = escape(' '.join(result.xpath('.//p//text()')))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # return results
    return results
