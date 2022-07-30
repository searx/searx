# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Stackoverflow (IT)
"""

from urllib.parse import urlencode, urljoin, urlparse
from lxml import html
from searx.utils import extract_text
from searx.exceptions import SearxEngineCaptchaException

# about
about = {
    "website": 'https://stackoverflow.com/',
    "wikidata_id": 'Q549037',
    "official_api_documentation": 'https://api.stackexchange.com/docs',
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

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
    resp_url = urlparse(resp.url)
    if resp_url.path.startswith('/nocaptcha'):
        raise SearxEngineCaptchaException()

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
