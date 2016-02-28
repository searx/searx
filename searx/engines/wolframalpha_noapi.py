# Wolfram|Alpha (Science)
#
# @website     https://www.wolframalpha.com/
# @provide-api yes (https://api.wolframalpha.com/v2/)
#
# @using-api   no
# @results     JSON
# @stable      no
# @parse       url, infobox

from cgi import escape
from json import loads
from time import time
from urllib import urlencode
from lxml.etree import XML

from searx.poolrequests import get as http_get

# search-url
url = 'https://www.wolframalpha.com/'

search_url = url + 'input/json.jsp'\
    '?async=true'\
    '&banners=raw'\
    '&debuggingdata=false'\
    '&format=image,plaintext,imagemap,minput,moutput'\
    '&formattimeout=2'\
    '&{query}'\
    '&output=JSON'\
    '&parsetimeout=2'\
    '&proxycode={token}'\
    '&scantimeout=0.5'\
    '&sponsorcategories=true'\
    '&statemethod=deploybutton'

referer_url = url + 'input/?{query}'

token = {'value': '',
         'last_updated': None}

# xpath variables
success_xpath = '/pod[attribute::error="false"]'
plaintext_xpath = './plaintext'
title_xpath = './@title'
image_xpath = './img'
img_src_xpath = './img/@src'
img_alt_xpath = './img/@alt'

# pods to display as image in infobox
# this pods do return a plaintext, but they look better and are more useful as images
image_pods = {'VisualRepresentation',
              'Illustration',
              'Symbol'}


# seems, wolframalpha resets its token in every hour
def obtain_token():
    update_time = time() - (time() % 3600)
    try:
        token_response = http_get('https://www.wolframalpha.com/input/api/v1/code?ts=9999999999999999999', timeout=2.0)
        token['value'] = loads(token_response.text)['code']
        token['last_updated'] = update_time
    except:
        pass
    return token


obtain_token()


# do search-request
def request(query, params):
    # obtain token if last update was more than an hour
    if time() - token['last_updated'] > 3600:
        obtain_token()
    params['url'] = search_url.format(query=urlencode({'input': query}), token=token['value'])
    params['headers']['Referer'] = referer_url.format(query=urlencode({'i': query}))

    return params


# get additional pod
# NOTE: this makes an additional requests to server, so the response will take longer and might reach timeout
def get_async_pod(url):
    try:
        resp = http_get(url, timeout=2.0)
    except:
        return None

    if resp:
        return parse_async_pod(resp)


def parse_async_pod(resp):
    pod = {'subpods': []}

    resp_pod = XML(resp.content)

    if resp_pod.xpath(success_xpath):
        for subpod in resp_pod:
            new_subpod = {'title': subpod.xpath(title_xpath)[0]}

            plaintext = subpod.xpath(plaintext_xpath)[0].text
            if plaintext:
                new_subpod['plaintext'] = plaintext
            else:
                new_subpod['plaintext'] = ''

            if subpod.xpath(image_xpath):
                new_subpod['img'] = {'src': subpod.xpath(img_src_xpath)[0],
                                     'alt': subpod.xpath(img_alt_xpath)[0]}

            pod['subpods'].append(new_subpod)

    return pod


# get response from search-request
def response(resp):
    results = []

    resp_json = loads(resp.text)

    if not resp_json['queryresult']['success']:
        return []

    # TODO handle resp_json['queryresult']['assumptions']
    result_chunks = []
    infobox_title = None
    for pod in resp_json['queryresult']['pods']:
        pod_id = pod.get('id', '')
        pod_title = pod.get('title', '')

        if 'subpods' not in pod:
            # comment this section if your requests always reach timeout
            if pod['async']:
                result = get_async_pod(pod['async'])
                if result:
                    pod = result
                else:
                    continue
            else:
                continue

        if pod_id == 'Input' or not infobox_title:
            infobox_title = pod['subpods'][0]['plaintext']

        for subpod in pod['subpods']:
            if subpod['plaintext'] != '' and pod_id not in image_pods:
                # append unless it's not an actual answer
                if subpod['plaintext'] != '(requires interactivity)':
                    result_chunks.append({'label': pod_title, 'value': subpod['plaintext']})

            elif 'img' in subpod:
                result_chunks.append({'label': pod_title, 'image': subpod['img']})

    if not result_chunks:
        return []

    results.append({'infobox': infobox_title,
                    'attributes': result_chunks,
                    'urls': [{'title': 'Wolfram|Alpha', 'url': resp.request.headers['Referer']}]})

    results.append({'url': resp.request.headers['Referer'],
                    'title': 'Wolfram|Alpha',
                    'content': infobox_title})

    return results
