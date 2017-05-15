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
from dateutil import parser
from datetime import datetime, timedelta
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
        params['data']['with_language'] = ('lang_' + params['language'].split('-')[0])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(results_xpath):
        links = result.xpath(link_xpath)
        if not links:
            continue
        link = links[0]
        url = link.attrib.get('href')

        # block google-ad url's
        if re.match(r"^http(s|)://(www\.)?google\.[a-z]+/aclk.*$", url):
            continue

        # block startpage search url's
        if re.match(r"^http(s|)://(www\.)?startpage\.com/do/search\?.*$", url):
            continue

        # block ixquick search url's
        if re.match(r"^http(s|)://(www\.)?ixquick\.com/do/search\?.*$", url):
            continue

        title = extract_text(link)

        if result.xpath('./p[@class="desc clk"]'):
            content = extract_text(result.xpath('./p[@class="desc clk"]'))
        else:
            content = ''

        published_date = None

        # check if search result starts with something like: "2 Sep 2014 ... "
        if re.match(r"^([1-9]|[1-2][0-9]|3[0-1]) [A-Z][a-z]{2} [0-9]{4} \.\.\. ", content):
            date_pos = content.find('...') + 4
            date_string = content[0:date_pos - 5]
            published_date = parser.parse(date_string, dayfirst=True)

            # fix content string
            content = content[date_pos:]

        # check if search result starts with something like: "5 days ago ... "
        elif re.match(r"^[0-9]+ days? ago \.\.\. ", content):
            date_pos = content.find('...') + 4
            date_string = content[0:date_pos - 5]

            # calculate datetime
            published_date = datetime.now() - timedelta(days=int(re.match(r'\d+', date_string).group()))

            # fix content string
            content = content[date_pos:]

        if published_date:
            # append result
            results.append({'url': url,
                            'title': title,
                            'content': content,
                            'publishedDate': published_date})
        else:
            # append result
            results.append({'url': url,
                            'title': title,
                            'content': content})

    # return results
    return results
