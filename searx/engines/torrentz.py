"""
 Torrentz.eu (BitTorrent meta-search engine)

 @website      https://torrentz.eu/
 @provide-api  no

 @using-api    no
 @results      HTML
 @stable       no (HTML can change, although unlikely,
                   see https://torrentz.eu/torrentz.btsearch)
 @parse        url, title, publishedDate, seed, leech, filesize, magnetlink
"""

import re
from urllib import urlencode
from lxml import html
from searx.engines.xpath import extract_text
from datetime import datetime
from searx.engines.nyaa import int_or_zero, get_filesize_mul

# engine dependent config
categories = ['files', 'videos', 'music']
paging = True

# search-url
# https://torrentz.eu/search?f=EXAMPLE&p=6
base_url = 'https://torrentz.eu/'
search_url = base_url + 'search?{query}'


# do search-request
def request(query, params):
    page = params['pageno'] - 1
    query = urlencode({'q': query, 'p': page})
    params['url'] = search_url.format(query=query)
    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    for result in dom.xpath('//div[@class="results"]/dl'):
        name_cell = result.xpath('./dt')[0]
        title = extract_text(name_cell)

        # skip rows that do not contain a link to a torrent
        links = name_cell.xpath('./a')
        if len(links) != 1:
            continue

        # extract url and remove a slash in the beginning
        link = links[0].attrib.get('href').lstrip('/')

        seed = result.xpath('./dd/span[@class="u"]/text()')[0].replace(',', '')
        leech = result.xpath('./dd/span[@class="d"]/text()')[0].replace(',', '')

        params = {
            'url': base_url + link,
            'title': title,
            'seed': int_or_zero(seed),
            'leech': int_or_zero(leech),
            'template': 'torrent.html'
        }

        # let's try to calculate the torrent size
        try:
            size_str = result.xpath('./dd/span[@class="s"]/text()')[0]
            size, suffix = size_str.split()
            params['filesize'] = int(size) * get_filesize_mul(suffix)
        except Exception as e:
            pass

        # does our link contain a valid SHA1 sum?
        if re.compile('[0-9a-fA-F]{40}').match(link):
            # add a magnet link to the result
            params['magnetlink'] = 'magnet:?xt=urn:btih:' + link

        # extract and convert creation date
        try:
            date_str = result.xpath('./dd/span[@class="a"]/span')[0].attrib.get('title')
            # Fri, 25 Mar 2016 16:29:01
            date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S')
            params['publishedDate'] = date
        except Exception as e:
            pass

        results.append(params)

    return results
