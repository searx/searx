## Twitter (Social media)
#
# @website     https://www.bing.com/news
# @provide-api yes (https://dev.twitter.com/docs/using-search)
#
# @using-api   no
# @results     HTML (using search portal)
# @stable      no (HTML can change)
# @parse       url, title, content
#
# @todo        publishedDate

from urlparse import urljoin
from urllib import urlencode
from lxml import html
from cgi import escape

# engine dependent config
categories = ['social media']
language_support = True

# search-url
base_url = 'https://twitter.com/'
search_url = base_url+'search?'

# specific xpath variables
results_xpath = '//li[@data-item-type="tweet"]'
link_xpath = './/small[@class="time"]//a'
title_xpath = './/span[@class="username js-action-profile-name"]//text()'
content_xpath = './/p[@class="js-tweet-text tweet-text"]//text()'


# do search-request
def request(query, params):
    params['url'] = search_url + urlencode({'q': query})

    # set language if specified
    if params['language'] != 'all':
        params['cookies']['lang'] = params['language'].split('_')[0]

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for tweet in dom.xpath(results_xpath):
        link = tweet.xpath(link_xpath)[0]
        url = urljoin(base_url, link.attrib.get('href'))
        title = ''.join(tweet.xpath(title_xpath))
        content = escape(''.join(tweet.xpath(content_xpath)))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # return results
    return results
