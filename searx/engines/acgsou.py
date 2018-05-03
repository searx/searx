"""
 Acgsou (Japanese Animation/Music/Comics Bittorrent tracker)

 @website      https://www.acgsou.com/
 @provide-api  no
 @using-api    no
 @results      HTML
 @stable       no (HTML can change)
 @parse        url, title, content, seed, leech, torrentfile
"""

from lxml import html
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode
from searx.utils import get_torrent_size, int_or_zero

# engine dependent config
categories = ['files', 'images', 'videos', 'music']
paging = True

# search-url
base_url = 'http://www.acgsou.com/'
search_url = base_url + 'search.php?{query}&page={offset}'
# xpath queries
xpath_results = '//table[contains(@class, "list_style table_fixed")]//tr[not(th)]'
xpath_category = './/td[2]/a[1]'
xpath_title = './/td[3]/a[last()]'
xpath_torrent_links = './/td[3]/a'
xpath_filesize = './/td[4]/text()'


def request(query, params):
    query = urlencode({'keyword': query})
    params['url'] = search_url.format(query=query, offset=params['pageno'])
    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    for result in dom.xpath(xpath_results):
        # defaults
        filesize = 0
        magnet_link = "magnet:?xt=urn:btih:{}&tr=http://tracker.acgsou.com:2710/announce"
        torrent_link = ""

        try:
            category = extract_text(result.xpath(xpath_category)[0])
        except:
            pass

        page_a = result.xpath(xpath_title)[0]
        title = extract_text(page_a)
        href = base_url + page_a.attrib.get('href')

        magnet_link = magnet_link.format(page_a.attrib.get('href')[5:-5])

        try:
            filesize_info = result.xpath(xpath_filesize)[0]
            filesize = filesize_info[:-2]
            filesize_multiplier = filesize_info[-2:]
            filesize = get_torrent_size(filesize, filesize_multiplier)
        except:
            pass
        # I didn't add download/seed/leech count since as I figured out they are generated randomly everytime
        content = 'Category: "{category}".'
        content = content.format(category=category)

        results.append({'url': href,
                        'title': title,
                        'content': content,
                        'filesize': filesize,
                        'magnetlink': magnet_link,
                        'template': 'torrent.html'})
    return results
