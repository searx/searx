"""
 Stackoverflow (It)

 @website     https://stackoverflow.com/
 @provide-api not clear (https://api.stackexchange.com/docs/advanced-search)

 @using-api   no
 @results     HTML
 @stable      no (HTML can change)
 @parse       url, title, content
"""

from lxml import html
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode, urljoin

# engine dependent config
categories = ['it']
paging = True

# search-url
url = 'https://stackoverflow.com/'
search_url = url + 'search?{query}&page={pageno}'

# specific xpath variables
results_xpath = '//div[contains(@class,"question-summary")]'
link_xpath = './/div[@class="result-link"]//a|.//div[@class="summary"]//h3//a'
content_xpath = './/div[@class="excerpt"]'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}), pageno=params['pageno'])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(results_xpath):
        link = result.xpath(link_xpath)[0]
        href = urljoin(url, link.attrib.get('href'))
        title = extract_text(link)
        content = extract_text(result.xpath(content_xpath))

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': content})

    # return results
    return results
