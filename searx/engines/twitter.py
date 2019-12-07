"""
 Twitter (Social media)

 @website     https://twitter.com/
 @provide-api yes (https://dev.twitter.com/docs/using-search)

 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content

 @todo        publishedDate
"""

from lxml import html
from datetime import datetime
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode, urljoin

# engine dependent config
categories = ['social media']
language_support = True

# search-url
base_url = 'https://twitter.com/'
search_url = base_url + 'search?'

# specific xpath variables
results_xpath = '//li[@data-item-type="tweet"]'
avatar_xpath = './/img[contains(@class, "avatar")]/@src'
link_xpath = './/small[@class="time"]//a'
title_xpath = './/span[contains(@class, "username")]'
content_xpath = './/p[contains(@class, "tweet-text")]'
timestamp_xpath = './/span[contains(@class,"_timestamp")]'


# do search-request
def request(query, params):
    params['url'] = search_url + urlencode({'q': query})

    # set language if specified
    if params['language'] != 'all':
        params['cookies']['lang'] = params['language'].split('-')[0]
    else:
        params['cookies']['lang'] = 'en'

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for tweet in dom.xpath(results_xpath):
        try:
            link = tweet.xpath(link_xpath)[0]
            content = extract_text(tweet.xpath(content_xpath)[0])
            img_src = tweet.xpath(avatar_xpath)[0]
            img_src = img_src.replace('_bigger', '_normal')
        except Exception:
            continue

        url = urljoin(base_url, link.attrib.get('href'))
        title = extract_text(tweet.xpath(title_xpath))

        pubdate = tweet.xpath(timestamp_xpath)
        if len(pubdate) > 0:
            timestamp = float(pubdate[0].attrib.get('data-time'))
            publishedDate = datetime.fromtimestamp(timestamp, None)
            # append result
            results.append({'url': url,
                            'title': title,
                            'content': content,
                            'img_src': img_src,
                            'publishedDate': publishedDate})
        else:
            # append result
            results.append({'url': url,
                            'title': title,
                            'content': content,
                            'img_src': img_src})

    # return results
    return results
