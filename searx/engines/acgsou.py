# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Acgsou (Japanese Animation/Music/Comics Bittorrent tracker)
"""

from urllib.parse import urlencode
from lxml import html
from searx.utils import extract_text, get_torrent_size, eval_xpath_list, eval_xpath_getindex

# about
about = {
    "website": 'https://www.acgsou.com/',
    "wikidata_id": None,
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['files', 'images', 'videos', 'music']
paging = True

# search-url
base_url = 'https://www.acgsou.com/'
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
    for result in eval_xpath_list(dom, xpath_results):
        # defaults
        filesize = 0
        magnet_link = "magnet:?xt=urn:btih:{}&tr=https://tracker.acgsou.com:2710/announce"

        category = extract_text(eval_xpath_getindex(result, xpath_category, 0, default=[]))
        page_a = eval_xpath_getindex(result, xpath_title, 0)
        title = extract_text(page_a)
        href = base_url + page_a.attrib.get('href')

        magnet_link = magnet_link.format(page_a.attrib.get('href')[5:-5])

        filesize_info = eval_xpath_getindex(result, xpath_filesize, 0, default=None)
        if filesize_info:
            try:
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
