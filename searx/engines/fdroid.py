"""
 F-Droid (a repository of FOSS applications for Android)

 @website      https://f-droid.org/
 @provide-api  no
 @using-api    no
 @results      HTML
 @stable       no (HTML can change)
 @parse        url, title, content
"""

from lxml import html
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode

# engine dependent config
categories = ['files']
paging = True

# search-url
base_url = 'https://search.f-droid.org/'
search_url = base_url + '?{query}'


# do search-request
def request(query, params):
    query = urlencode({'q': query, 'page': params['pageno'], 'lang': ''})
    params['url'] = search_url.format(query=query)
    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    for app in dom.xpath('//a[@class="package-header"]'):
        app_url = app.xpath('./@href')[0]
        app_title = extract_text(app.xpath('./div/h4[@class="package-name"]/text()'))
        app_content = extract_text(app.xpath('./div/div/span[@class="package-summary"]')).strip() \
            + ' - ' + extract_text(app.xpath('./div/div/span[@class="package-license"]')).strip()
        app_img_src = app.xpath('./img[@class="package-icon"]/@src')[0]

        results.append({'url': app_url,
                        'title': app_title,
                        'content': app_content,
                        'img_src': app_img_src})

    return results
