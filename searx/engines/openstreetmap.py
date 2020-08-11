"""
 OpenStreetMap (Map)

 @website     https://openstreetmap.org/
 @provide-api yes (http://wiki.openstreetmap.org/wiki/Nominatim)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title
"""

import re
from json import loads
from flask_babel import gettext

# engine dependent config
categories = ['map']
paging = False

# search-url
base_url = 'https://nominatim.openstreetmap.org/'
search_string = 'search/{query}?format=json&polygon_geojson=1&addressdetails=1'
result_base_url = 'https://openstreetmap.org/{osm_type}/{osm_id}'

route_url = 'https://graphhopper.com/maps/?point={}&point={}&locale=en-US&vehicle=car&weighting=fastest&turn_costs=true&use_miles=false&layer=Omniscale'  # noqa
route_re = re.compile('(?:from )?(.+) to (.+)')


# do search-request
def request(query, params):

    params['url'] = base_url + search_string.format(query=query)
    params['route'] = route_re.match(query)

    return params


# get response from search-request
def response(resp):
    results = []
    json = loads(resp.text)

    if resp.search_params['route']:
        results.append({
            'answer': gettext('Get directions'),
            'url': route_url.format(*resp.search_params['route'].groups()),
        })

    # parse results
    for r in json:
        if 'display_name' not in r:
            continue

        title = r['display_name'] or ''
        osm_type = r.get('osm_type', r.get('type'))
        url = result_base_url.format(osm_type=osm_type,
                                     osm_id=r['osm_id'])

        osm = {'type': osm_type,
               'id': r['osm_id']}

        geojson = r.get('geojson')

        # if no geojson is found and osm_type is a node, add geojson Point
        if not geojson and osm_type == 'node':
            geojson = {'type': 'Point', 'coordinates': [r['lon'], r['lat']]}

        address_raw = r.get('address')
        address = {}

        # get name
        if r['class'] == 'amenity' or\
           r['class'] == 'shop' or\
           r['class'] == 'tourism' or\
           r['class'] == 'leisure':
            if address_raw.get('address29'):
                address = {'name': address_raw.get('address29')}
            else:
                address = {'name': address_raw.get(r['type'])}

        # add rest of adressdata, if something is already found
        if address.get('name'):
            address.update({'house_number': address_raw.get('house_number'),
                           'road': address_raw.get('road'),
                           'locality': address_raw.get('city',
                                       address_raw.get('town',          # noqa
                                       address_raw.get('village'))),    # noqa
                           'postcode': address_raw.get('postcode'),
                           'country': address_raw.get('country'),
                           'country_code': address_raw.get('country_code')})
        else:
            address = None

        # append result
        results.append({'template': 'map.html',
                        'title': title,
                        'content': '',
                        'longitude': r['lon'],
                        'latitude': r['lat'],
                        'boundingbox': r['boundingbox'],
                        'geojson': geojson,
                        'address': address,
                        'osm': osm,
                        'url': url})

    # return results
    return results
