"""
 APK Mirror

 @website     https://www.apkmirror.com

 @using-api   no
 @results     HTML
 @stable      no (HTML can change)
 @parse       url, title, thumbnail_src
"""

from lxml import html
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode

# engine dependent config
categories = ['it']
paging = True

# I am not 100% certain about this, as apkmirror appears to be a wordpress site,
# which might support time_range searching. If you want to implement it, go ahead.
time_range_support = False

# search-url
base_url = 'https://www.apkmirror.com'
search_url = base_url + '/?post_type=app_release&searchtype=apk&page={pageno}&{query}'


# do search-request
def request(query, params):

    params['url'] = search_url.format(pageno=params['pageno'],
                                      query=urlencode({'s': query}))
    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath('.//div[@id="content"]/div[@class="listWidget"]/div[@class="appRow"]'):

        link = result.xpath('.//h5/a')[0]
        url = base_url + link.attrib.get('href') + '#downloads'
        title = extract_text(link)
        thumbnail_src = base_url + result.xpath('.//img')[0].attrib.get('src').replace('&w=32&h=32', '&w=64&h=64')

        res = {
            'url': url,
            'title': title,
            'thumbnail_src': thumbnail_src
        }

        # append result
        results.append(res)

    # return results
    return results
