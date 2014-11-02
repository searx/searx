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
url = 'https://nominatim.openstreetmap.org/search/{query}?format=json&polygon_geojson=1'

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

        geojson =  r.get('geojson')

        # if no geojson is found and osm_type is a node, add geojson Point
        if not geojson and\
           osm_type == 'node':
            geojson = {u'type':u'Point', 
                       u'coordinates':[r['lon'],r['lat']]}

        # append result
        results.append({'template': 'map.html',
                        'title': title,
                        'content': '',
                        'longitude': r['lon'],
                        'latitude': r['lat'],
                        'boundingbox': r['boundingbox'],
                        'geojson': geojson,
                        'url': url})

    # return results
    return results
