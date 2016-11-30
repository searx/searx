"""
 BTDigg (Videos, Music, Files)

 @website     https://btdigg.org
 @provide-api yes (on demand)

 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content, seed, leech, magnetlink
"""

from lxml import html
from operator import itemgetter
from searx.engines.xpath import extract_text
from searx.url_utils import quote, urljoin
from searx.utils import get_torrent_size

# engine dependent config
categories = ['videos', 'music', 'files']
paging = True

# search-url
url = 'https://btdigg.org'
search_url = url + '/search?q={search_term}&p={pageno}'


# do search-request
def request(query, params):
    params['url'] = search_url.format(search_term=quote(query),
                                      pageno=params['pageno'] - 1)

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    search_res = dom.xpath('//div[@id="search_res"]/table/tr')

    # return empty array if nothing is found
    if not search_res:
        return []

    # parse results
    for result in search_res:
        link = result.xpath('.//td[@class="torrent_name"]//a')[0]
        href = urljoin(url, link.attrib.get('href'))
        title = extract_text(link)
        content = extract_text(result.xpath('.//pre[@class="snippet"]')[0])
        content = "<br />".join(content.split("\n"))

        filesize = result.xpath('.//span[@class="attr_val"]/text()')[0].split()[0]
        filesize_multiplier = result.xpath('.//span[@class="attr_val"]/text()')[0].split()[1]
        files = result.xpath('.//span[@class="attr_val"]/text()')[1]
        seed = result.xpath('.//span[@class="attr_val"]/text()')[2]

        # convert seed to int if possible
        if seed.isdigit():
            seed = int(seed)
        else:
            seed = 0

        leech = 0

        # convert filesize to byte if possible
        filesize = get_torrent_size(filesize, filesize_multiplier)

        # convert files to int if possible
        if files.isdigit():
            files = int(files)
        else:
            files = None

        magnetlink = result.xpath('.//td[@class="ttth"]//a')[0].attrib['href']

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': content,
                        'seed': seed,
                        'leech': leech,
                        'filesize': filesize,
                        'files': files,
                        'magnetlink': magnetlink,
                        'template': 'torrent.html'})

    # return results sorted by seeder
    return sorted(results, key=itemgetter('seed'), reverse=True)
