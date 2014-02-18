from urllib import urlencode
from lxml import html

base_url = None
search_url = None

# TODO paging
paging = False
# TODO complete list of country mapping
country_map = {'en_US': 'eng',
               'en_UK': 'uk',
               'nl_NL': 'ned'}


def request(query, params):
    query = urlencode({'q': query})[2:]
    params['url'] = search_url
    params['method'] = 'POST'
    params['data'] = {'query': query,
                      'startat': (params['pageno'] - 1) * 10}  # offset
    country = country_map.get(params['language'], 'eng')
    params['cookies']['preferences'] = \
        'lang_homepageEEEs/air/{country}/N1NsslEEE1N1Nfont_sizeEEEmediumN1Nrecent_results_filterEEE1N1Nlanguage_uiEEEenglishN1Ndisable_open_in_new_windowEEE0N1Ncolor_schemeEEEnewN1Nnum_of_resultsEEE10N1N'.format(country=country)  # noqa
    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.content)
    # ads xpath //div[@id="results"]/div[@id="sponsored"]//div[@class="result"]
    # not ads: div[@class="result"] are the direct childs of div[@id="results"]
    for result in dom.xpath('//div[@class="result"]'):
        link = result.xpath('.//h3/a')[0]
        url = link.attrib.get('href')
        if url.startswith('http://www.google.')\
           or url.startswith('https://www.google.'):
            continue
        title = link.text_content()

        content = ''
        if result.xpath('./p[@class="desc"]'):
            content = result.xpath('./p[@class="desc"]')[0].text_content()

        results.append({'url': url, 'title': title, 'content': content})

    return results
