"""
 Kickass Torrent (Videos, Music, Files)

 @website     https://kickass.so
 @provide-api no (nothing found)

 @using-api   no
 @results     HTML (using search portal)
 @stable      yes (HTML can change)
 @parse       url, title, content, seed, leech, magnetlink
"""

from lxml import html
from operator import itemgetter
from searx.engines.xpath import extract_text
from searx.utils import get_torrent_size, convert_str_to_int
from searx.url_utils import quote, urljoin

# engine dependent config
categories = ['videos', 'music', 'files']
paging = True

# search-url
url = 'https://kickass.cd/'
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
        content = extract_text(result.xpath(content_xpath))
        seed = extract_text(result.xpath('.//td[contains(@class, "green")]'))
        leech = extract_text(result.xpath('.//td[contains(@class, "red")]'))
        filesize_info = extract_text(result.xpath('.//td[contains(@class, "nobr")]'))
        files = extract_text(result.xpath('.//td[contains(@class, "center")][2]'))

        seed = convert_str_to_int(seed)
        leech = convert_str_to_int(leech)

        filesize, filesize_multiplier = filesize_info.split()
        filesize = get_torrent_size(filesize, filesize_multiplier)
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
