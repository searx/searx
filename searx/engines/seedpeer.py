#  Seedpeer (Videos, Music, Files)
#
# @website     http://seedpeer.eu
# @provide-api no (nothing found)
#
# @using-api   no
# @results     HTML (using search portal)
# @stable      yes (HTML can change)
# @parse       url, title, content, seed, leech, magnetlink

from lxml import html
from operator import itemgetter
from searx.url_utils import quote, urljoin


url = 'http://www.seedpeer.eu/'
search_url = url + 'search/{search_term}/7/{page_no}.html'
# specific xpath variables
torrent_xpath = '//*[@id="body"]/center/center/table[2]/tr/td/a'
alternative_torrent_xpath = '//*[@id="body"]/center/center/table[1]/tr/td/a'
title_xpath = '//*[@id="body"]/center/center/table[2]/tr/td/a/text()'
alternative_title_xpath = '//*[@id="body"]/center/center/table/tr/td/a'
seeds_xpath = '//*[@id="body"]/center/center/table[2]/tr/td[4]/font/text()'
alternative_seeds_xpath = '//*[@id="body"]/center/center/table/tr/td[4]/font/text()'
peers_xpath = '//*[@id="body"]/center/center/table[2]/tr/td[5]/font/text()'
alternative_peers_xpath = '//*[@id="body"]/center/center/table/tr/td[5]/font/text()'
age_xpath = '//*[@id="body"]/center/center/table[2]/tr/td[2]/text()'
alternative_age_xpath = '//*[@id="body"]/center/center/table/tr/td[2]/text()'
size_xpath = '//*[@id="body"]/center/center/table[2]/tr/td[3]/text()'
alternative_size_xpath = '//*[@id="body"]/center/center/table/tr/td[3]/text()'


# do search-request
def request(query, params):
    params['url'] = search_url.format(search_term=quote(query),
                                      page_no=params['pageno'] - 1)
    return params


# get response from search-request
def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    torrent_links = dom.xpath(torrent_xpath)
    if len(torrent_links) > 0:
        seeds = dom.xpath(seeds_xpath)
        peers = dom.xpath(peers_xpath)
        titles = dom.xpath(title_xpath)
        sizes = dom.xpath(size_xpath)
        ages = dom.xpath(age_xpath)
    else:  # under ~5 results uses a different xpath
        torrent_links = dom.xpath(alternative_torrent_xpath)
        seeds = dom.xpath(alternative_seeds_xpath)
        peers = dom.xpath(alternative_peers_xpath)
        titles = dom.xpath(alternative_title_xpath)
        sizes = dom.xpath(alternative_size_xpath)
        ages = dom.xpath(alternative_age_xpath)
    # return empty array if nothing is found
    if not torrent_links:
        return []

    # parse results
    for index, result in enumerate(torrent_links):
        link = result.attrib.get('href')
        href = urljoin(url, link)
        results.append({'url': href,
                        'title': titles[index].text_content(),
                        'content': '{}, {}'.format(sizes[index], ages[index]),
                        'seed': seeds[index],
                        'leech': peers[index],

                        'template': 'torrent.html'})

    # return results sorted by seeder
    return sorted(results, key=itemgetter('seed'), reverse=True)
