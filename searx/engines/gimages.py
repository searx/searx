#!/usr/bin/env python

from urllib import quote
from lxml import html
from urlparse import urljoin

categories = ['images']

base_url = 'https://www.google.com/'
search_url = base_url+'search?tbm=isch&hl=en&q='

def request(query, params):
    global search_url
    query = quote(query.replace(' ', '+'), safe='+')
    params['url'] = search_url + query
    return params

def response(resp):
    global base_url
    results = []
    dom = html.fromstring(resp.text)
    for result in dom.xpath('//table[@class="images_table"]//a'):
        url = urljoin(base_url, result.attrib.get('href'))
        img = result.xpath('.//img')[0]
        title = ' '.join(result.xpath('..//text()'))
        content = '<img src="%s" alt="%s" />' % (img.attrib.get('src', ''), title)
        results.append({'url': url, 'title': title, 'content': content})
    return results
