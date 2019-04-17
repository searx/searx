"""
 Deviantart (Images)

 @website     https://www.deviantart.com/
 @provide-api yes (https://www.deviantart.com/developers/) (RSS)

 @using-api   yes
 @results     RSS
 @stable      yes
 @parse       url, title, thumbnail_src, img_src

 @todo        rewrite to api
"""

from lxml import etree
import re
import os.path
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode, unquote

# engine dependent config
categories = ['images']
paging = True
time_range_support = True
number_of_results = 24

# search-url
base_url = 'https://backend.deviantart.com/'
search_url = base_url + 'rss.xml?type=deviation'\
    '&{query}'\
    '&{offset}'
time_range_url = '&order={range}'

time_range_dict = {'day': 11,
                   'week': 14,
                   'month': 15}

strip_tags_re = re.compile(r'<[^>]*?>')


# do search-request
def request(query, params):
    if params['time_range'] and params['time_range'] not in time_range_dict:
        return params

    offset = (params['pageno'] - 1) * number_of_results

    params['url'] = search_url.format(offset=offset,
                                      query=urlencode({'q': query}))
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_url.format(range=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    rss = etree.fromstring(resp.content)
    ns = rss.nsmap

    # parse results
    for item in rss.xpath('./channel/item'):

        # find largest thumbnail
        thumbnail_area = 0
        for thumbnail in item.xpath('./media:thumbnail', namespaces=ns):
            t_width = int(thumbnail.xpath('./@width')[0])
            t_height = int(thumbnail.xpath('./@height')[0])
            if (t_width * t_height) > thumbnail_area:
                thumbnail_area = t_width * t_height
                thumbnail_src = thumbnail.xpath('./@url')[0]

        # could also used 'guid' which seems to contain a permalink
        url = item.xpath('./link/text()')[0]

        # the choice is between 'title' and 'media:title', they seem to contain the same data
        # so choose the former
        title = item.xpath('./title/text()')[0]

        img_src = item.xpath('./media:content/@url', namespaces=ns)[0]

        # media:content has a 'medium' attribute but it always contains the rather
        # non-descriptive term 'image', instead extract the extension from the
        # img_src url instead to get something more descriptive.
        img_format = "{0} {1}x{2}".format(\
            os.path.splitext(item.xpath('./media:content/@url', namespaces=ns)[0])[1][1:],\
            str(item.xpath('./media:content/@width', namespaces=ns)[0]),
            str(item.xpath('./media:content/@height', namespaces=ns)[0]))
       
        content = re.sub(strip_tags_re, '', unquote(item.xpath('./description/text()')[0]))
        source = item.xpath('./media:copyright/text()', namespaces=ns)[0]
        author = item.xpath('./media:credit', namespaces=ns)[0].xpath('text()')[0]

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'thumbnail_src': thumbnail_src,
                        'img_format': img_format,
                        'source': source,
                        'content': content,
                        'author': author,
                        'template': 'images.html'})

    return results
