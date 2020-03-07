#  Seedpeer (Videos, Music, Files)
#
# @website     https://seedpeer.me
# @provide-api no (nothing found)
#
# @using-api   no
# @results     HTML (using search portal)
# @stable      yes (HTML can change)
# @parse       url, title, content, seed, leech, magnetlink

from lxml import html
from json import loads
from operator import itemgetter
from searx.url_utils import quote, urljoin
from searx.engines.xpath import extract_text


url = 'https://seedpeer.me/'
search_url = url + 'search/{search_term}?page={page_no}'
torrent_file_url = url + 'torrent/{torrent_hash}'

# specific xpath variables
script_xpath = '//script[@type="text/javascript"][not(@src)]'
torrent_xpath = '(//table)[2]/tbody/tr'
link_xpath = '(./td)[1]/a/@href'
age_xpath = '(./td)[2]'
size_xpath = '(./td)[3]'


# do search-request
def request(query, params):
    params['url'] = search_url.format(search_term=quote(query),
                                      page_no=params['pageno'])
    return params


# get response from search-request
def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    result_rows = dom.xpath(torrent_xpath)

    try:
        script_element = dom.xpath(script_xpath)[0]
        json_string = script_element.text[script_element.text.find('{'):]
        torrents_json = loads(json_string)
    except:
        return []

    # parse results
    for torrent_row, torrent_json in zip(result_rows, torrents_json['data']['list']):
        title = torrent_json['name']
        seed = int(torrent_json['seeds'])
        leech = int(torrent_json['peers'])
        size = int(torrent_json['size'])
        torrent_hash = torrent_json['hash']

        torrentfile = torrent_file_url.format(torrent_hash=torrent_hash)
        magnetlink = 'magnet:?xt=urn:btih:{}'.format(torrent_hash)

        age = extract_text(torrent_row.xpath(age_xpath))
        link = torrent_row.xpath(link_xpath)[0]

        href = urljoin(url, link)

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': age,
                        'seed': seed,
                        'leech': leech,
                        'filesize': size,
                        'torrentfile': torrentfile,
                        'magnetlink': magnetlink,
                        'template': 'torrent.html'})

    # return results sorted by seeder
    return sorted(results, key=itemgetter('seed'), reverse=True)
