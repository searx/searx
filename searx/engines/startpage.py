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

from lxml import html
from dateutil import parser
from datetime import datetime, timedelta
import re
from searx.engines.xpath import extract_text
import logging

# engine dependent config
categories = ['general']
# there is a mechanism to block "bot" search
# (probably the parameter qid), require
# storing of qid's between mulitble search-calls

paging = True
language_support = True

# search-url
base_url = 'https://startpage.com/'
search_url = base_url + 'do/search'

# specific xpath variables
# ads xpath //div[@id="results"]/div[@id="sponsored"]//div[@class="result"]
# not ads: div[@class="result"] are the direct childs of div[@id="results"]
results_xpath = '//li[contains(@class, "search-result") and contains(@class, "search-item")]'
link_xpath = './/h3/a'
content_xpath = './p[@class="search-item__body"]'
qid_xpath = '//input[@name="qid"]/@value'
cat_xpath = '//input[@name="cat"]/@value'

logger = logging.getLogger('Startpage')


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10

    params['url'] = search_url
    params['method'] = 'POST'
    if len(params['qid']) < 2:
        params['data'] = {'query': query,
                          'startat': offset}
    else:
        params['data'] = {'query': query,
                          'startat': offset,
                          'qid': params['qid'],
                          'cat': params['cat']}

    # set language if specified
    if params['language'] != 'all':
        params['data']['with_language'] = ('lang_' + params['language'].split('-')[0])
    logger.debug(params)

    return params


# get response from search-request
def response(resp):
    results = []
    engine_attributes = dict()

    dom = html.fromstring(resp.text)

    if dom.xpath(qid_xpath):
        qid = dom.xpath(qid_xpath)
        engine_attributes["qid"] = qid[0]

    if dom.xpath(cat_xpath):
        cat = dom.xpath(cat_xpath)
        engine_attributes["cat"] = cat[0]

    results.append({"engine_attributes": engine_attributes})

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

        title = extract_text(link)

        if result.xpath(content_xpath):
            content = extract_text(result.xpath(content_xpath))
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
