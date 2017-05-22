"""
 Bing (News)

 @website     https://www.bing.com/news
 @provide-api yes (http://datamarket.azure.com/dataset/bing/search),
              max. 5000 query/month

 @using-api   no (because of query limit)
 @results     RSS (using search portal)
 @stable      yes (except perhaps for the images)
 @parse       url, title, content, publishedDate, thumbnail
"""

from datetime import datetime
from dateutil import parser
from lxml import etree
from searx.utils import list_get
from searx.engines.bing import _fetch_supported_languages, supported_languages_url
from searx.url_utils import urlencode, urlparse, parse_qsl

# engine dependent config
categories = ['news']
paging = True
language_support = True
time_range_support = True

# search-url
base_url = 'https://www.bing.com/'
search_string = 'news/search?{query}&first={offset}&format=RSS'
search_string_with_time = 'news/search?{query}&first={offset}&qft=interval%3d"{interval}"&format=RSS'
time_range_dict = {'day': '7',
                   'week': '8',
                   'month': '9'}


# remove click
def url_cleanup(url_string):
    parsed_url = urlparse(url_string)
    if parsed_url.netloc == 'www.bing.com' and parsed_url.path == '/news/apiclick.aspx':
        query = dict(parse_qsl(parsed_url.query))
        return query.get('url', None)
    return url_string


# replace the http://*bing4.com/th?id=... by https://www.bing.com/th?id=...
def image_url_cleanup(url_string):
    parsed_url = urlparse(url_string)
    if parsed_url.netloc.endswith('bing4.com') and parsed_url.path == '/th':
        query = dict(parse_qsl(parsed_url.query))
        return "https://www.bing.com/th?id=" + query.get('id')
    return url_string


def _get_url(query, language, offset, time_range):
    if time_range in time_range_dict:
        search_path = search_string_with_time.format(
            query=urlencode({'q': query, 'setmkt': language}),
            offset=offset,
            interval=time_range_dict[time_range])
    else:
        search_path = search_string.format(
            query=urlencode({'q': query, 'setmkt': language}),
            offset=offset)
    return base_url + search_path


# do search-request
def request(query, params):
    if params['time_range'] and params['time_range'] not in time_range_dict:
        return params

    offset = (params['pageno'] - 1) * 10 + 1

    if params['language'] == 'all':
        language = 'en-US'
    else:
        language = params['language']

    params['url'] = _get_url(query, language, offset, params['time_range'])

    return params


# get response from search-request
def response(resp):
    results = []

    rss = etree.fromstring(resp.content)

    ns = rss.nsmap

    # parse results
    for item in rss.xpath('./channel/item'):
        # url / title / content
        url = url_cleanup(item.xpath('./link/text()')[0])
        title = list_get(item.xpath('./title/text()'), 0, url)
        content = list_get(item.xpath('./description/text()'), 0, '')

        # publishedDate
        publishedDate = list_get(item.xpath('./pubDate/text()'), 0)
        try:
            publishedDate = parser.parse(publishedDate, dayfirst=False)
        except TypeError:
            publishedDate = datetime.now()
        except ValueError:
            publishedDate = datetime.now()

        # thumbnail
        thumbnail = list_get(item.xpath('./News:Image/text()', namespaces=ns), 0)
        if thumbnail is not None:
            thumbnail = image_url_cleanup(thumbnail)

        # append result
        if thumbnail is not None:
            results.append({'url': url,
                            'title': title,
                            'publishedDate': publishedDate,
                            'content': content,
                            'img_src': thumbnail})
        else:
            results.append({'url': url,
                            'title': title,
                            'publishedDate': publishedDate,
                            'content': content})

    # return results
    return results
