#  Piratebay (Videos, Music, Files)
#
# @website     https://thepiratebay.se
# @provide-api no (nothing found)
#
# @using-api   no
# @results     HTML (using search portal)
# @stable      yes (HTML can change)
# @parse       url, title, content, seed, leech, magnetlink

from lxml import html
from operator import itemgetter
from searx.engines.xpath import extract_text
from searx.url_utils import quote, urljoin

# engine dependent config
categories = ['videos', 'music', 'files']
paging = True

# search-url
url = 'https://thepiratebay.se/'
search_url = url + 'search/{search_term}/{pageno}/99/{search_type}'

# piratebay specific type-definitions
search_types = {'files': '0',
                'music': '100',
                'videos': '200'}

# specific xpath variables
magnet_xpath = './/a[@title="Download this torrent using magnet"]'
torrent_xpath = './/a[@title="Download this torrent"]'
content_xpath = './/font[@class="detDesc"]'


# do search-request
def request(query, params):
    search_type = search_types.get(params['category'], '0')

    params['url'] = search_url.format(search_term=quote(query),
                                      search_type=search_type,
                                      pageno=params['pageno'] - 1)

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    search_res = dom.xpath('//table[@id="searchResult"]//tr')

    # return empty array if nothing is found
    if not search_res:
        return []

    # parse results
    for result in search_res[1:]:
        link = result.xpath('.//div[@class="detName"]//a')[0]
        href = urljoin(url, link.attrib.get('href'))
        title = extract_text(link)
        content = extract_text(result.xpath(content_xpath))
        seed, leech = result.xpath('.//td[@align="right"]/text()')[:2]

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

        magnetlink = result.xpath(magnet_xpath)[0]
        torrentfile_links = result.xpath(torrent_xpath)
        if torrentfile_links:
            torrentfile_link = torrentfile_links[0].attrib.get('href')
        else:
            torrentfile_link = None

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': content,
                        'seed': seed,
                        'leech': leech,
                        'magnetlink': magnetlink.attrib.get('href'),
                        'torrentfile': torrentfile_link,
                        'template': 'torrent.html'})

    # return results sorted by seeder
    return sorted(results, key=itemgetter('seed'), reverse=True)
