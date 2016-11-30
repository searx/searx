# Youtube (Videos)
#
# @website     https://www.youtube.com/
# @provide-api yes (https://developers.google.com/apis-explorer/#p/youtube/v3/youtube.search.list)
#
# @using-api   no
# @results     HTML
# @stable      no
# @parse       url, title, content, publishedDate, thumbnail, embedded

from lxml import html
from searx.engines.xpath import extract_text
from searx.utils import list_get
from searx.url_utils import quote_plus

# engine dependent config
categories = ['videos', 'music']
paging = True
language_support = False
time_range_support = True

# search-url
base_url = 'https://www.youtube.com/results'
search_url = base_url + '?search_query={query}&page={page}'
time_range_url = '&sp=EgII{time_range}%253D%253D'
time_range_dict = {'day': 'Ag',
                   'week': 'Aw',
                   'month': 'BA',
                   'year': 'BQ'}

embedded_url = '<iframe width="540" height="304" ' +\
    'data-src="//www.youtube-nocookie.com/embed/{videoid}" ' +\
    'frameborder="0" allowfullscreen></iframe>'

base_youtube_url = 'https://www.youtube.com/watch?v='

# specific xpath variables
results_xpath = "//ol/li/div[contains(@class, 'yt-lockup yt-lockup-tile yt-lockup-video vve-check')]"
url_xpath = './/h3/a/@href'
title_xpath = './/div[@class="yt-lockup-content"]/h3/a'
content_xpath = './/div[@class="yt-lockup-content"]/div[@class="yt-lockup-description yt-ui-ellipsis yt-ui-ellipsis-2"]'


# returns extract_text on the first result selected by the xpath or None
def extract_text_from_dom(result, xpath):
    r = result.xpath(xpath)
    if len(r) > 0:
        return extract_text(r[0])
    return None


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=quote_plus(query),
                                      page=params['pageno'])
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_url.format(time_range=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(results_xpath):
        videoid = list_get(result.xpath('@data-context-item-id'), 0)
        if videoid is not None:
            url = base_youtube_url + videoid
            thumbnail = 'https://i.ytimg.com/vi/' + videoid + '/hqdefault.jpg'

            title = extract_text_from_dom(result, title_xpath) or videoid
            content = extract_text_from_dom(result, content_xpath)

            embedded = embedded_url.format(videoid=videoid)

            # append result
            results.append({'url': url,
                            'title': title,
                            'content': content,
                            'template': 'videos.html',
                            'embedded': embedded,
                            'thumbnail': thumbnail})

    # return results
    return results
