from urllib import urlencode
from cgi import escape
from lxml import html

base_url = 'http://www.bing.com/'
search_string = 'search?{query}&first={offset}'
paging = True
language_support = True


def request(query, params):
    offset = (params['pageno'] - 1) * 10 + 1
    if params['language'] == 'all':
        language = 'en-US'
    else:
        language = params['language'].replace('_', '-')
    search_path = search_string.format(
        query=urlencode({'q': query, 'setmkt': language}),
        offset=offset)

    params['cookies']['SRCHHPGUSR'] = \
        'NEWWND=0&NRSLT=-1&SRCHLANG=' + language.split('-')[0]
    #if params['category'] == 'images':
    #    params['url'] = base_url + 'images/' + search_path
    params['url'] = base_url + search_path
    return params


def response(resp):
    global base_url
    results = []
    dom = html.fromstring(resp.content)
    for result in dom.xpath('//div[@class="sa_cc"]'):
        link = result.xpath('.//h3/a')[0]
        url = link.attrib.get('href')
        title = ' '.join(link.xpath('.//text()'))
        content = escape(' '.join(result.xpath('.//p//text()')))
        results.append({'url': url, 'title': title, 'content': content})

    if results:
        return results

    for result in dom.xpath('//li[@class="b_algo"]'):
        link = result.xpath('.//h2/a')[0]
        url = link.attrib.get('href')
        title = ' '.join(link.xpath('.//text()'))
        content = escape(' '.join(result.xpath('.//p//text()')))
        results.append({'url': url, 'title': title, 'content': content})
    return results
