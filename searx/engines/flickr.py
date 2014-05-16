#!/usr/bin/env python

from urllib import urlencode
from json import loads
#from urlparse import urljoin

categories = ['images']

# url = 'https://secure.flickr.com/'
# search_url = url+'search/?{query}&page={page}'
# results_xpath = '//div[@id="thumbnails"]//a[@class="rapidnofollow photo-click" and @data-track="photo-click"]'  # noqa

paging = True

# text=[query]
# TODO clean "extras"
search_url = 'https://api.flickr.com/services/rest?extras=can_addmeta%2Ccan_comment%2Ccan_download%2Ccan_share%2Ccontact%2Ccount_comments%2Ccount_faves%2Ccount_notes%2Cdate_taken%2Cdate_upload%2Cdescription%2Cicon_urls_deep%2Cisfavorite%2Cispro%2Clicense%2Cmedia%2Cneeds_interstitial%2Cowner_name%2Cowner_datecreate%2Cpath_alias%2Crealname%2Csafety_level%2Csecret_k%2Csecret_h%2Curl_c%2Curl_h%2Curl_k%2Curl_l%2Curl_m%2Curl_n%2Curl_o%2Curl_q%2Curl_s%2Curl_sq%2Curl_t%2Curl_z%2Cvisibility&per_page=50&page={page}&{query}&sort=relevance&method=flickr.photos.search&api_key=ad11b34c341305471e3c410a02e671d0&format=json'  # noqa


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'text': query}),
                                      page=params['pageno'])
    #params['url'] = search_url.format(query=urlencode({'q': query}),
    #                                  page=params['pageno'])
    return params


def response(resp):
    results = []
    images = loads(resp.text[14:-1])["photos"]["photo"]
    for i in images:
        results.append({'url': i['url_s'],
                        'title': i['title'],
                        'img_src': i['url_s'],
                        'template': 'images.html'})
    #dom = html.fromstring(resp.text)
    #for result in dom.xpath(results_xpath):
    #    href = urljoin(url, result.attrib.get('href'))
    #    img = result.xpath('.//img')[0]
    #    title = img.attrib.get('alt', '')
    #    img_src = img.attrib.get('data-defer-src')
    #    if not img_src:
    #        continue
    #    results.append({'url': href,
    #                    'title': title,
    #                    'img_src': img_src,
    #                    'template': 'images.html'})
    return results
