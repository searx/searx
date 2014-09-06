## OpenStreetMap (Map)
#
# @website     https://openstreetmap.org/
# @provide-api yes (http://wiki.openstreetmap.org/wiki/Nominatim)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title

from json import loads

# engine dependent config
categories = ['map']
paging = False

# search-url
url = 'https://nominatim.openstreetmap.org/search/{query}?format=json'

result_base_url = 'https://openstreetmap.org/{osm_type}/{osm_id}'


# do search-request
def request(query, params):
    params['url'] = url.format(query=query)

    return params


# get response from search-request
def response(resp):
    results = []
    json = loads(resp.text)

    # parse results
    for r in json:
        title = r['display_name']
        osm_type = r.get('osm_type', r.get('type'))
        url = result_base_url.format(osm_type=osm_type,
                                     osm_id=r['osm_id'])
        # append result
        results.append({'title': title,
                        'content': '',
                        'url': url})

    # return results
    return results
