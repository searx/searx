from lxml import html
from searx.engines.xpath import extract_text
from searx.utils import get_torrent_size
from searx.url_utils import quote, urljoin

url = 'https://1337x.to/'
search_url = url + 'search/{search_term}/{pageno}/'
categories = ['videos']
paging = True


def request(query, params):
    params['url'] = search_url.format(search_term=quote(query), pageno=params['pageno'])

    return params


def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    for result in dom.xpath('//table[contains(@class, "table-list")]/tbody//tr'):
        href = urljoin(url, result.xpath('./td[contains(@class, "name")]/a[2]/@href')[0])
        title = extract_text(result.xpath('./td[contains(@class, "name")]/a[2]'))
        seed = extract_text(result.xpath('.//td[contains(@class, "seeds")]'))
        leech = extract_text(result.xpath('.//td[contains(@class, "leeches")]'))
        filesize_info = extract_text(result.xpath('.//td[contains(@class, "size")]/text()'))
        filesize, filesize_multiplier = filesize_info.split()
        filesize = get_torrent_size(filesize, filesize_multiplier)

        results.append({'url': href,
                        'title': title,
                        'seed': seed,
                        'leech': leech,
                        'filesize': filesize,
                        'template': 'torrent.html'})

    return results
