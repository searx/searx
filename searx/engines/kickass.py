"""
 Kickass Torrent (Videos, Music, Files)

 @website     https://kickass.so
 @provide-api no (nothing found)

 @using-api   no
 @results     HTML (using search portal)
 @stable      yes (HTML can change)
 @parse       url, title, content, seed, leech, magnetlink
"""

from urlparse import urljoin
from cgi import escape
from urllib import quote
from lxml import html
from operator import itemgetter
from searx.engines.xpath import extract_text

# engine dependent config
categories = ['videos', 'music', 'files']
paging = True

# search-url
url = 'https://kickass.to/'
search_url = url + 'search/{search_term}/{pageno}/'

# specific xpath variables
magnet_xpath = './/a[@title="Torrent magnet link"]'
torrent_xpath = './/a[@title="Download torrent file"]'
content_xpath = './/span[@class="font11px lightgrey block"]'


# do search-request
def request(query, params):
    params['url'] = search_url.format(search_term=quote(query),
                                      pageno=params['pageno'])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    search_res = dom.xpath('//table[@class="data"]//tr')

    # return empty array if nothing is found
    if not search_res:
        return []

    # parse results
    for result in search_res[1:]:
        link = result.xpath('.//a[@class="cellMainLink"]')[0]
        href = urljoin(url, link.attrib['href'])
        title = extract_text(link)
        content = escape(extract_text(result.xpath(content_xpath)))
        seed = result.xpath('.//td[contains(@class, "green")]/text()')[0]
        leech = result.xpath('.//td[contains(@class, "red")]/text()')[0]
        filesize = result.xpath('.//td[contains(@class, "nobr")]/text()')[0]
        filesize_multiplier = result.xpath('.//td[contains(@class, "nobr")]//span/text()')[0]
        files = result.xpath('.//td[contains(@class, "center")][2]/text()')[0]

        # convert seed to int if possible
        if seed.isdigit():
            seed = int(seed)
        else:
            seed = 0

        # convert leech to int if possible
        if leech.isdigit():
            leech = int(leech)
        else:
            leech = 0

        # convert filesize to byte if possible
        try:
            filesize = float(filesize)

            # convert filesize to byte
            if filesize_multiplier == 'TB':
                filesize = int(filesize * 1024 * 1024 * 1024 * 1024)
            elif filesize_multiplier == 'GB':
                filesize = int(filesize * 1024 * 1024 * 1024)
            elif filesize_multiplier == 'MB':
                filesize = int(filesize * 1024 * 1024)
            elif filesize_multiplier == 'KB':
                filesize = int(filesize * 1024)
        except:
            filesize = None

        # convert files to int if possible
        if files.isdigit():
            files = int(files)
        else:
            files = None

        magnetlink = result.xpath(magnet_xpath)[0].attrib['href']

        torrentfile = result.xpath(torrent_xpath)[0].attrib['href']
        torrentfileurl = quote(torrentfile, safe="%/:=&?~#+!$,;'@()*")

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': content,
                        'seed': seed,
                        'leech': leech,
                        'filesize': filesize,
                        'files': files,
                        'magnetlink': magnetlink,
                        'torrentfile': torrentfileurl,
                        'template': 'torrent.html'})

    # return results sorted by seeder
    return sorted(results, key=itemgetter('seed'), reverse=True)
