from urlparse import urljoin
from urllib import urlencode
from lxml import html

categories = ['social media']

base_url = 'https://twitter.com/'
search_url = base_url+'search?'

def request(query, params):
    global search_url
    params['url'] = search_url + urlencode({'q': query})
    return params


def response(resp):
    global base_url
    results = []
    dom = html.fromstring(resp.text)
    for tweet in dom.xpath('//li[@data-item-type="tweet"]'):
        link = tweet.xpath('.//small[@class="time"]//a')[0]
        url = urljoin(base_url, link.attrib.get('href'))
        title = ''.join(tweet.xpath('.//span[@class="username js-action-profile-name"]//text()'))
        content = ''.join(map(html.tostring, tweet.xpath('.//p[@class="js-tweet-text tweet-text"]//*')))
        results.append({'url': url, 'title': title, 'content': content})
    return results
