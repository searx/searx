# Youtube (Videos)
#
# @website     https://www.youtube.com/
# @provide-api yes (https://developers.google.com/apis-explorer/#p/youtube/v3/youtube.search.list)
#
# @using-api   no
# @results     HTML
# @stable      no
# @parse       url, title, content, publishedDate, thumbnail, embedded

from functools import reduce
from json import loads
from urllib.parse import quote_plus

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
    'data-src="https://www.youtube-nocookie.com/embed/{videoid}" ' +\
    'frameborder="0" allowfullscreen></iframe>'

base_youtube_url = 'https://www.youtube.com/watch?v='


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

    results_data = resp.text[resp.text.find('ytInitialData'):]
    results_data = results_data[results_data.find('{'):results_data.find(';</script>')]

    results_json = loads(results_data) if results_data else {}
    sections = results_json.get('contents', {})\
                           .get('twoColumnSearchResultsRenderer', {})\
                           .get('primaryContents', {})\
                           .get('sectionListRenderer', {})\
                           .get('contents', [])

    for section in sections:
        for video_container in section.get('itemSectionRenderer', {}).get('contents', []):
            video = video_container.get('videoRenderer', {})
            videoid = video.get('videoId')
            if videoid is not None:
                url = base_youtube_url + videoid
                thumbnail = 'https://i.ytimg.com/vi/' + videoid + '/hqdefault.jpg'
                title = get_text_from_json(video.get('title', {}))
                content = get_text_from_json(video.get('descriptionSnippet', {}))
                embedded = embedded_url.format(videoid=videoid)
                author = get_text_from_json(video.get('ownerText', {}))
                length = get_text_from_json(video.get('lengthText', {}))

                # append result
                results.append({'url': url,
                                'title': title,
                                'content': content,
                                'author': author,
                                'length': length,
                                'template': 'videos.html',
                                'embedded': embedded,
                                'thumbnail': thumbnail})

    # return results
    return results


def get_text_from_json(element):
    if 'runs' in element:
        return reduce(lambda a, b: a + b.get('text', ''), element.get('runs'), '')
    else:
        return element.get('simpleText', '')
