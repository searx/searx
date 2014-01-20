from urllib import urlencode
from lxml import html
from json import loads

categories = ['videos']
locale = 'en_US'

# see http://www.dailymotion.com/doc/api/obj-video.html
search_url = 'https://api.dailymotion.com/videos?fields=title,description,duration,url,thumbnail_360_url&sort=relevance&limit=25&page=1&{query}'  # noqa

# TODO use video result template
content_tpl = '<a href="{0}" title="{0}" ><img src="{1}" /></a><br />'


def request(query, params):
    global search_url
    params['url'] = search_url.format(
        query=urlencode({'search': query, 'localization': locale}))
    return params


def response(resp):
    results = []
    search_res = loads(resp.text)
    if not 'list' in search_res:
        return results
    for res in search_res['list']:
        title = res['title']
        url = res['url']
        if res['thumbnail_360_url']:
            content = content_tpl.format(url, res['thumbnail_360_url'])
        else:
            content = ''
        if res['description']:
            description = text_content_from_html(res['description'])
            content += description[:500]
        results.append({'url': url, 'title': title, 'content': content})
    return results


def text_content_from_html(html_string):
    desc_html = html.fragment_fromstring(html_string, create_parent=True)
    return desc_html.text_content()
