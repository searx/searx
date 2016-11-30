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
base_url = 'https://f-droid.org/'
search_url = base_url + 'repository/browse/?{query}'


# do search-request
def request(query, params):
    query = urlencode({'fdfilter': query, 'fdpage': params['pageno']})
    params['url'] = search_url.format(query=query)
    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    for app in dom.xpath('//div[@id="appheader"]'):
        url = app.xpath('./ancestor::a/@href')[0]
        title = app.xpath('./p/span/text()')[0]
        img_src = app.xpath('.//img/@src')[0]

        content = extract_text(app.xpath('./p')[0])
        content = content.replace(title, '', 1).strip()

        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'img_src': img_src})

    return results
