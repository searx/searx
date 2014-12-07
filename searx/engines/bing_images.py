## Bing (Images)
#
# @website     https://www.bing.com/images
# @provide-api yes (http://datamarket.azure.com/dataset/bing/search),
#              max. 5000 query/month
#
# @using-api   no (because of query limit)
# @results     HTML (using search portal)
# @stable      no (HTML can change)
# @parse       url, title, img_src
#
# @todo        currently there are up to 35 images receive per page,
#              because bing does not parse count=10.
#              limited response to 10 images

from urllib import urlencode
from lxml import html
from yaml import load
import re

# engine dependent config
categories = ['images']
paging = True

# search-url
base_url = 'https://www.bing.com/'
search_string = 'images/search?{query}&count=10&first={offset}'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10 + 1

    # required for cookie
    language = 'en-US'

    search_path = search_string.format(
        query=urlencode({'q': query}),
        offset=offset)

    params['cookies']['SRCHHPGUSR'] = \
        'NEWWND=0&NRSLT=-1&SRCHLANG=' + language.split('-')[0]

    params['url'] = base_url + search_path

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.content)

    # init regex for yaml-parsing
    p = re.compile('({|,)([a-z]+):(")')

    # parse results
    for result in dom.xpath('//div[@class="dg_u"]'):
        link = result.xpath('./a')[0]

        # parse yaml-data (it is required to add a space, to make it parsable)
        yaml_data = load(p.sub(r'\1\2: \3', link.attrib.get('m')))

        title = link.attrib.get('t1')
        #url = 'http://' + link.attrib.get('t3')
        url = yaml_data.get('surl')
        img_src = yaml_data.get('imgurl')

        # append result
        results.append({'template': 'images.html',
                        'url': url,
                        'title': title,
                        'content': '',
                        'img_src': img_src})

        # TODO stop parsing if 10 images are found
        if len(results) >= 10:
            break

    # return results
    return results
