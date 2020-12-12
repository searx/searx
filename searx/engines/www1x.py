"""
 1x (Images)

 @website     http://1x.com/
 @provide-api no

 @using-api   no
 @results     HTML
 @stable      no (HTML can change)
 @parse       url, title, thumbnail
"""

from lxml import html, etree
from urllib.parse import urlencode, urljoin
from searx.utils import extract_text, eval_xpath_list, eval_xpath_getindex

# engine dependent config
categories = ['images']
paging = False

# search-url
base_url = 'https://1x.com'
search_url = base_url + '/backend/search.php?{query}'
gallery_url = 'https://gallery.1x.com/'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}))

    return params


# get response from search-request
def response(resp):
    results = []
    xmldom = etree.fromstring(resp.content)
    xmlsearchresult = eval_xpath_getindex(xmldom, '//searchresult', 0)
    dom = html.fragment_fromstring(xmlsearchresult.text, create_parent='div')
    for link in eval_xpath_list(dom, '/div/table/tr/td/div[2]//a'):
        url = urljoin(base_url, link.attrib.get('href'))
        title = extract_text(link)
        thumbnail_src = urljoin(gallery_url, eval_xpath_getindex(link, './/img', 0).attrib['src'])

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': thumbnail_src,
                        'content': '',
                        'thumbnail_src': thumbnail_src,
                        'template': 'images.html'})

    # return results
    return results
