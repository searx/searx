#  Startpage (Web)
#
# @website     https://startpage.com
# @provide-api no (nothing found)
#
# @using-api   no
# @results     HTML
# @stable      no (HTML can change)
# @parse       url, title, content
#
# @todo        paging

from lxml import html
from cgi import escape
import re
from searx.engines.xpath import extract_text

# engine dependent config
categories = ['general']
# there is a mechanism to block "bot" search
# (probably the parameter qid), require
# storing of qid's between mulitble search-calls

# paging = False
language_support = True

# search-url
base_url = 'https://startpage.com/'
search_url = base_url + 'do/search'

# specific xpath variables
# ads xpath //div[@id="results"]/div[@id="sponsored"]//div[@class="result"]
# not ads: div[@class="result"] are the direct childs of div[@id="results"]
results_xpath = '//div[@class="result"]'
link_xpath = './/h3/a'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10

    params['url'] = search_url
    params['method'] = 'POST'
    params['data'] = {'query': query,
                      'startat': offset}

    # set language if specified
    if params['language'] != 'all':
        params['data']['with_language'] = ('lang_' + params['language'].split('_')[0])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.content)

    # parse results
    for result in dom.xpath(results_xpath):
        links = result.xpath(link_xpath)
        if not links:
            continue
        link = links[0]
        url = link.attrib.get('href')

        # block google-ad url's
        if re.match("^http(s|)://(www\.)?google\.[a-z]+/aclk.*$", url):
            continue

        # block startpage search url's
        if re.match("^http(s|)://(www\.)?startpage\.com/do/search\?.*$", url):
            continue

        # block ixquick search url's
        if re.match("^http(s|)://(www\.)?ixquick\.com/do/search\?.*$", url):
            continue

        title = escape(extract_text(link))

        if result.xpath('./p[@class="desc"]'):
            content = escape(extract_text(result.xpath('./p[@class="desc"]')))
        else:
            content = ''

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # return results
    return results
