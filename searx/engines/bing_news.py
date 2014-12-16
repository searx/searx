## Bing (News)
#
# @website     https://www.bing.com/news
# @provide-api yes (http://datamarket.azure.com/dataset/bing/search),
#              max. 5000 query/month
#
# @using-api   no (because of query limit)
# @results     HTML (using search portal)
# @stable      no (HTML can change)
# @parse       url, title, content, publishedDate

from urllib import urlencode
from cgi import escape
from lxml import html
from datetime import datetime, timedelta
from dateutil import parser
import re

# engine dependent config
categories = ['news']
paging = True
language_support = True

# search-url
base_url = 'https://www.bing.com/'
search_string = 'news/search?{query}&first={offset}'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10 + 1

    if params['language'] == 'all':
        language = 'en-US'
    else:
        language = params['language'].replace('_', '-')

    search_path = search_string.format(
        query=urlencode({'q': query, 'setmkt': language}),
        offset=offset)

    params['cookies']['SRCHHPGUSR'] = \
        'NEWWND=0&NRSLT=-1&SRCHLANG=' + language.split('-')[0]

    params['url'] = base_url + search_path
    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.content)

    # parse results
    for result in dom.xpath('//div[@class="sn_r"]'):
        link = result.xpath('.//div[@class="newstitle"]/a')[0]
        url = link.attrib.get('href')
        title = ' '.join(link.xpath('.//text()'))
        contentXPath = result.xpath('.//div[@class="sn_txt"]/div'
                                    '//span[@class="sn_snip"]//text()')
        if contentXPath is not None:
            content = escape(' '.join(contentXPath))

        # parse publishedDate
        publishedDateXPath = result.xpath('.//div[@class="sn_txt"]/div'
                                          '//span[contains(@class,"sn_ST")]'
                                          '//span[contains(@class,"sn_tm")]'
                                          '//text()')
        if publishedDateXPath is not None:
            publishedDate = escape(' '.join(publishedDateXPath))

        if re.match("^[0-9]+ minute(s|) ago$", publishedDate):
            timeNumbers = re.findall(r'\d+', publishedDate)
            publishedDate = datetime.now()\
                - timedelta(minutes=int(timeNumbers[0]))
        elif re.match("^[0-9]+ hour(s|) ago$", publishedDate):
            timeNumbers = re.findall(r'\d+', publishedDate)
            publishedDate = datetime.now()\
                - timedelta(hours=int(timeNumbers[0]))
        elif re.match("^[0-9]+ hour(s|),"
                      " [0-9]+ minute(s|) ago$", publishedDate):
            timeNumbers = re.findall(r'\d+', publishedDate)
            publishedDate = datetime.now()\
                - timedelta(hours=int(timeNumbers[0]))\
                - timedelta(minutes=int(timeNumbers[1]))
        elif re.match("^[0-9]+ day(s|) ago$", publishedDate):
            timeNumbers = re.findall(r'\d+', publishedDate)
            publishedDate = datetime.now()\
                - timedelta(days=int(timeNumbers[0]))
        else:
            try:
                # FIXME use params['language'] to parse either mm/dd or dd/mm
                publishedDate = parser.parse(publishedDate, dayfirst=False)
            except TypeError:
                # FIXME
                publishedDate = datetime.now()

        # append result
        results.append({'url': url,
                        'title': title,
                        'publishedDate': publishedDate,
                        'content': content})

    # return results
    return results
