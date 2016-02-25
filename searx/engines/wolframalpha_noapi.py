# WolframAlpha (Maths)
#
# @website     http://www.wolframalpha.com/
# @provide-api yes (http://api.wolframalpha.com/v2/)
#
# @using-api   no
# @results     HTML
# @stable      no
# @parse       answer

from cgi import escape
from json import loads
from time import time
from urllib import urlencode

from searx.poolrequests import get as http_get

# search-url
url = 'https://www.wolframalpha.com/'
search_url = url + 'input/?{query}'

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

# xpath variables
scripts_xpath = '//script'
title_xpath = '//title'
failure_xpath = '//p[attribute::class="pfail"]'
token = {'value': '',
         'last_updated': None}


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
    params['headers']['Referer'] = 'https://www.wolframalpha.com/input/?i=' + query

    return params


# get response from search-request
def response(resp):
    resp_json = loads(resp.text)

    if not resp_json['queryresult']['success']:
        return []

    # TODO handle resp_json['queryresult']['assumptions']
    result_chunks = []
    for pod in resp_json['queryresult']['pods']:
        pod_title = pod.get('title', '')
        if 'subpods' not in pod:
            continue
        for subpod in pod['subpods']:
            if 'img' in subpod:
                result_chunks.append(u'<p>{0}<br /><img src="{1}" alt="{2}" /></p>'
                                     .format(escape(pod_title or subpod['img']['alt']),
                                             escape(subpod['img']['src']),
                                             escape(subpod['img']['alt'])))

    if not result_chunks:
        return []

    return [{'url': resp.request.headers['Referer'].decode('utf-8'),
             'title': 'Wolframalpha',
             'content': ''.join(result_chunks)}]
