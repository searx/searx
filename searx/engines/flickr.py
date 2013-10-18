#!/usr/bin/env python

from urllib import quote
from lxml import html
from urlparse import urljoin

categories = ['img']

base_url = 'https://secure.flickr.com/'
search_url = base_url+'search/?q='

def request(query, params):
    global search_url
    print 'qqwerqwerqwerqwer'
    query = quote(query.replace(' ', '+'), safe='+')
    params['url'] = search_url + query
    return params

def response(resp):
    global base_url
    print 'asdfasdfasdf'
    results = []
    dom = html.fromstring(resp.text)
    for result in dom.xpath('//#thumbnails//a'):
        url = urljoin(base_url, result.attrib.get('href'))
        title = result.xpath('./img')[0].attrib.get('alt')
        content = "<img src='%s'></img>" % result.xpath('./img')[0].attrib.get('src')
        results.append({'url': url, 'title': title, 'content': content})
    return results
