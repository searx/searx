## Kickass Torrent (Videos, Music, Files)
#
# @website     https://kickass.so
# @provide-api no (nothing found)
#
# @using-api   no
# @results     HTML (using search portal)
# @stable      yes (HTML can change)
# @parse       url, title, content, seed, leech, magnetlink

from urlparse import urljoin
from cgi import escape
from urllib import quote
from lxml import html
from operator import itemgetter

# engine dependent config
categories = ['videos', 'music', 'files']
paging = True

# search-url
url = 'https://kickass.so/'
search_url = url + 'search/{search_term}/{pageno}/'

# specific xpath variables
magnet_xpath = './/a[@title="Torrent magnet link"]'
#content_xpath = './/font[@class="detDesc"]//text()'


# do search-request
def request(query, params):
    params['url'] = search_url.format(search_term=quote(query),
                                      pageno=params['pageno'])

    # FIX: SSLError: hostname 'kickass.so'
    # doesn't match either of '*.kickass.to', 'kickass.to'
    params['verify'] = False

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
        title = ' '.join(link.xpath('.//text()'))
        content = escape(html.tostring(result.xpath('.//span[@class="font11px lightgrey block"]')[0], method="text"))
        seed = result.xpath('.//td[contains(@class, "green")]/text()')[0]
        leech = result.xpath('.//td[contains(@class, "red")]/text()')[0]

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

        magnetlink = result.xpath(magnet_xpath)[0].attrib['href']

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': content,
                        'seed': seed,
                        'leech': leech,
                        'magnetlink': magnetlink,
                        'template': 'torrent.html'})

    # return results sorted by seeder
    return sorted(results, key=itemgetter('seed'), reverse=True)
