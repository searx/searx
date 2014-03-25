#!/usr/bin/env python

from urllib import urlencode
from lxml import html
from searx.engines.xpath import extract_text, extract_url
from searx.engines.yahoo import parse_url
from datetime import datetime, timedelta
import re
from dateutil import parser

categories = ['news']
search_url = 'http://news.search.yahoo.com/search?{query}&b={offset}'
results_xpath = '//div[@class="res"]'
url_xpath = './/h3/a/@href'
title_xpath = './/h3/a'
content_xpath = './/div[@class="abstr"]'
publishedDate_xpath = './/span[@class="timestamp"]'
suggestion_xpath = '//div[@id="satat"]//a'

paging = True


def request(query, params):
    offset = (params['pageno'] - 1) * 10 + 1
    if params['language'] == 'all':
        language = 'en'
    else:
        language = params['language'].split('_')[0]
    params['url'] = search_url.format(offset=offset,
                                      query=urlencode({'p': query}))
    params['cookies']['sB'] = 'fl=1&vl=lang_{lang}&sh=1&rw=new&v=1'\
        .format(lang=language)
    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)

    for result in dom.xpath(results_xpath):
        url = parse_url(extract_url(result.xpath(url_xpath), search_url))
        title = extract_text(result.xpath(title_xpath)[0])
        content = extract_text(result.xpath(content_xpath)[0])
        publishedDate = extract_text(result.xpath(publishedDate_xpath)[0])

        if re.match("^[0-9]+ minute(s|) ago$", publishedDate):
            publishedDate = datetime.now() - timedelta(minutes=int(re.match(r'\d+', publishedDate).group()))  # noqa
        else:
            if re.match("^[0-9]+ hour(s|), [0-9]+ minute(s|) ago$",
                        publishedDate):
                timeNumbers = re.findall(r'\d+', publishedDate)
                publishedDate = datetime.now()\
                    - timedelta(hours=int(timeNumbers[0]))\
                    - timedelta(minutes=int(timeNumbers[1]))
            else:
                publishedDate = parser.parse(publishedDate)

        if publishedDate.year == 1900:
            publishedDate = publishedDate.replace(year=datetime.now().year)

        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'publishedDate': publishedDate})

    if not suggestion_xpath:
        return results

    for suggestion in dom.xpath(suggestion_xpath):
        results.append({'suggestion': extract_text(suggestion)})

    return results
