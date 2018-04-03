"""
 Recoll (local search engine)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, content, size, abstract, author, mtype, time, filename, label
"""

from json import loads
from searx.url_utils import urlencode
from datetime import date, timedelta

# engine dependent config
paging = True
time_range_support = True

# parameters from settings.yml
base_url = None
search_dir = ''
dl_prefix = None


def get_time_range(time_range):
    sw = {
        'day': 1,
        'week': 7,
        'month': 30,
        'year': 365
    }

    offset = sw.get(time_range, 0)
    if not offset:
        return ''

    return (date.today()-timedelta(days=offset)).isoformat()


# do search-request
def request(query, params):
    search_after = get_time_range(params['time_range'])
    search_url = base_url + 'json?query={query}&page={page}&after={after}&dir={dir}&highlight=0'

    params['url'] = search_url.format(query=urlencode({'q': query}), page=params['pageno'],
                                      after=search_after, dir=search_dir)

    return params


# get response from search-request
def response(resp):
    results = []

    raw_search_results = loads(resp.text)

    if not raw_search_results:
        return []

    for result in raw_search_results.get('results', []):
        title = result['label']
        url = result['url'].replace('file:///export', dl_prefix)
        content = u'{}'.format(result['snippet'])

        # append result
        item = {'url': url,
                'title': title,
                'content': content,
                'template': 'files.html'}

        if result['size']:
            item['size'] = int(result['size'])

        for parameter in ['filename', 'abstract', 'author', 'mtype', 'time']:
            if result[parameter]:
                item[parameter] = result[parameter]

        results.append(item)

    return results
