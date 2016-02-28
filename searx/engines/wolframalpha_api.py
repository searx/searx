# Wolfram Alpha (Science)
#
# @website     https://www.wolframalpha.com
# @provide-api yes (https://api.wolframalpha.com/v2/)
#
# @using-api   yes
# @results     XML
# @stable      yes
# @parse       url, infobox

from urllib import urlencode
from lxml import etree

# search-url
search_url = 'https://api.wolframalpha.com/v2/query?appid={api_key}&{query}'
site_url = 'https://www.wolframalpha.com/input/?{query}'
api_key = ''  # defined in settings.yml

# xpath variables
failure_xpath = '/queryresult[attribute::success="false"]'
answer_xpath = '//pod[attribute::primary="true"]/subpod/plaintext'
input_xpath = '//pod[starts-with(attribute::title, "Input")]/subpod/plaintext'
pods_xpath = '//pod'
subpods_xpath = './subpod'
pod_title_xpath = './@title'
plaintext_xpath = './plaintext'
image_xpath = './img'
img_src_xpath = './@src'
img_alt_xpath = './@alt'

# pods to display as image in infobox
# this pods do return a plaintext, but they look better and are more useful as images
image_pods = {'Visual representation',
              'Manipulatives illustration'}


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'input': query}),
                                      api_key=api_key)
    params['headers']['Referer'] = site_url.format(query=urlencode({'i': query}))

    return params


# replace private user area characters to make text legible
def replace_pua_chars(text):
    pua_chars = {u'\uf522': u'\u2192',
                 u'\uf7b1': u'\u2115',
                 u'\uf7b4': u'\u211a',
                 u'\uf7b5': u'\u211d',
                 u'\uf7bd': u'\u2124',
                 u'\uf74c': 'd',
                 u'\uf74d': u'\u212f',
                 u'\uf74e': 'i',
                 u'\uf7d9': '='}

    for k, v in pua_chars.iteritems():
        text = text.replace(k, v)

    return text


# get response from search-request
def response(resp):
    results = []

    search_results = etree.XML(resp.content)

    # return empty array if there are no results
    if search_results.xpath(failure_xpath):
        return []

    infobox_title = search_results.xpath(input_xpath)
    if infobox_title:
        infobox_title = replace_pua_chars(infobox_title[0].text)

    pods = search_results.xpath(pods_xpath)
    result_chunks = []
    for pod in pods:
        pod_title = replace_pua_chars(pod.xpath(pod_title_xpath)[0])

        subpods = pod.xpath(subpods_xpath)
        if not subpods:
            continue

        for subpod in subpods:
            content = subpod.xpath(plaintext_xpath)[0].text
            image = subpod.xpath(image_xpath)
            if content and pod_title not in image_pods:
                content = replace_pua_chars(content)
                result_chunks.append({'label': pod_title, 'value': content})

                # if there's no input pod, infobox_title is content of first pod
                if not infobox_title:
                    infobox_title = content

            elif image:
                result_chunks.append({'label': pod_title,
                                      'image': {'src': image[0].xpath(img_src_xpath)[0],
                                                'alt': image[0].xpath(img_alt_xpath)[0]}})

    if not result_chunks:
        return []

    results.append({'infobox': infobox_title,
                    'attributes': result_chunks,
                    'urls': [{'title': 'Wolfram|Alpha', 'url': resp.request.headers['Referer']}]})

    # append link to site
    results.append({'url': resp.request.headers['Referer'],
                    'title': 'Wolfram|Alpha',
                    'content': infobox_title})

    return results
