"""
 Tokyo Toshokan (A BitTorrent Library for Japanese Media)

 @website      https://www.tokyotosho.info/
 @provide-api  no
 @using-api    no
 @results      HTML
 @stable       no (HTML can change)
 @parse        url, title, publishedDate, seed, leech,
               filesize, magnetlink, content
"""

import re
from lxml import html
from searx.engines.xpath import extract_text
from datetime import datetime
from searx.url_utils import urlencode
from searx.utils import get_torrent_size, int_or_zero

# engine dependent config
categories = ['files', 'videos', 'music']
paging = True

# search-url
base_url = 'https://www.tokyotosho.info/'
search_url = base_url + 'search.php?{query}'


# do search-request
def request(query, params):
    query = urlencode({'page': params['pageno'], 'terms': query})
    params['url'] = search_url.format(query=query)
    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)
    rows = dom.xpath('//table[@class="listing"]//tr[contains(@class, "category_0")]')

    # check if there are no results or page layout was changed so we cannot parse it
    # currently there are two rows for each result, so total count must be even
    if len(rows) == 0 or len(rows) % 2 != 0:
        return []

    # regular expression for parsing torrent size strings
    size_re = re.compile(r'Size:\s*([\d.]+)(TB|GB|MB|B)', re.IGNORECASE)

    # processing the results, two rows at a time
    for i in range(0, len(rows), 2):
        # parse the first row
        name_row = rows[i]

        links = name_row.xpath('./td[@class="desc-top"]/a')
        params = {
            'template': 'torrent.html',
            'url': links[-1].attrib.get('href'),
            'title': extract_text(links[-1])
        }
        # I have not yet seen any torrents without magnet links, but
        # it's better to be prepared to stumble upon one some day
        if len(links) == 2:
            magnet = links[0].attrib.get('href')
            if magnet.startswith('magnet'):
                # okay, we have a valid magnet link, let's add it to the result
                params['magnetlink'] = magnet

        # no more info in the first row, start parsing the second one
        info_row = rows[i + 1]
        desc = extract_text(info_row.xpath('./td[@class="desc-bot"]')[0])
        for item in desc.split('|'):
            item = item.strip()
            if item.startswith('Size:'):
                try:
                    # ('1.228', 'GB')
                    groups = size_re.match(item).groups()
                    params['filesize'] = get_torrent_size(groups[0], groups[1])
                except:
                    pass
            elif item.startswith('Date:'):
                try:
                    # Date: 2016-02-21 21:44 UTC
                    date = datetime.strptime(item, 'Date: %Y-%m-%d %H:%M UTC')
                    params['publishedDate'] = date
                except:
                    pass
            elif item.startswith('Comment:'):
                params['content'] = item
        stats = info_row.xpath('./td[@class="stats"]/span')
        # has the layout not changed yet?
        if len(stats) == 3:
            params['seed'] = int_or_zero(extract_text(stats[0]))
            params['leech'] = int_or_zero(extract_text(stats[1]))

        results.append(params)

    return results
