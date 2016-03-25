"""
 Nyaa.se (Anime Bittorrent tracker)

 @website      http://www.nyaa.se/
 @provide-api  no
 @using-api    no
 @results      HTML
 @stable       no (HTML can change)
 @parse        url, title, content, seed, leech, torrentfile
"""

from cgi import escape
from urllib import urlencode
from lxml import html
from searx.engines.xpath import extract_text

# engine dependent config
categories = ['files', 'images', 'videos', 'music']
paging = True

# search-url
base_url = 'http://www.nyaa.se/'
search_url = base_url + '?page=search&{query}&offset={offset}'

# xpath queries
xpath_results = '//table[@class="tlist"]//tr[contains(@class, "tlistrow")]'
xpath_category = './/td[@class="tlisticon"]/a'
xpath_title = './/td[@class="tlistname"]/a'
xpath_torrent_file = './/td[@class="tlistdownload"]/a'
xpath_filesize = './/td[@class="tlistsize"]/text()'
xpath_seeds = './/td[@class="tlistsn"]/text()'
xpath_leeches = './/td[@class="tlistln"]/text()'
xpath_downloads = './/td[@class="tlistdn"]/text()'


# convert a variable to integer or return 0 if it's not a number
def int_or_zero(num):
    if isinstance(num, list):
        if len(num) < 1:
            return 0
        num = num[0]
    if num.isdigit():
        return int(num)
    return 0

# get multiplier to convert torrent size to bytes
def get_filesize_mul(suffix):
    return {
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,

        'KIB': 1024,
        'MIB': 1024 ** 2,
        'GIB': 1024 ** 3,
        'TIB': 1024 ** 4
    }[str(suffix).upper()]

# do search-request
def request(query, params):
    query = urlencode({'term': query})
    params['url'] = search_url.format(query=query, offset=params['pageno'])
    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    for result in dom.xpath(xpath_results):
        # category in which our torrent belongs
        category = result.xpath(xpath_category)[0].attrib.get('title')

        # torrent title
        page_a = result.xpath(xpath_title)[0]
        title = escape(extract_text(page_a))

        # link to the page
        href = page_a.attrib.get('href')

        # link to the torrent file
        torrent_link = result.xpath(xpath_torrent_file)[0].attrib.get('href')

        # torrent size
        try:
            file_size, suffix = result.xpath(xpath_filesize)[0].split(' ')
            file_size = int(float(file_size) * get_filesize_mul(suffix))
        except Exception as e:
            file_size = None

        # seed count
        seed = int_or_zero(result.xpath(xpath_seeds))

        # leech count
        leech = int_or_zero(result.xpath(xpath_leeches))

        # torrent downloads count
        downloads = int_or_zero(result.xpath(xpath_downloads))

        # content string contains all information not included into template
        content = 'Category: "{category}". Downloaded {downloads} times.'
        content = content.format(category=category, downloads=downloads)
        content = escape(content)

        results.append({'url': href,
                        'title': title,
                        'content': content,
                        'seed': seed,
                        'leech': leech,
                        'filesize': file_size,
                        'torrentfile': torrent_link,
                        'template': 'torrent.html'})

    return results
