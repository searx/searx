# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import openstreetmap
from searx.testing import SearxTestCase


class TestOpenstreetmapEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = openstreetmap.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('openstreetmap.org', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, openstreetmap.response, None)
        self.assertRaises(AttributeError, openstreetmap.response, [])
        self.assertRaises(AttributeError, openstreetmap.response, '')
        self.assertRaises(AttributeError, openstreetmap.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(openstreetmap.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(openstreetmap.response(response), [])

        json = """
        [
          {
            "place_id": "127732055",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://www.openstreetmap.org/copyright",
            "osm_type": "relation",
            "osm_id": "7444",
            "boundingbox": [
              "48.8155755",
              "48.902156",
              "2.224122",
              "2.4697602"
            ],
            "lat": "48.8565056",
            "lon": "2.3521334",
            "display_name": "This is the title",
            "class": "place",
            "type": "city",
            "importance": 0.96893459932191,
            "icon": "https://nominatim.openstreetmap.org/images/mapicons/poi_place_city.p.20.png",
            "address": {
              "city": "Paris",
              "county": "Paris",
              "state": "Île-de-France",
              "country": "France",
              "country_code": "fr"
            },
            "geojson": {
              "type": "Polygon",
              "coordinates": [
                [
                  [
                    2.224122,
                    48.854199
                  ]
                ]
              ]
            }
          }
        ]
        """
        response = mock.Mock(text=json)
        results = openstreetmap.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://openstreetmap.org/relation/7444')
        self.assertIn('coordinates', results[0]['geojson'])
        self.assertEqual(results[0]['geojson']['coordinates'][0][0][0], 2.224122)
        self.assertEqual(results[0]['geojson']['coordinates'][0][0][1], 48.854199)
        self.assertEqual(results[0]['address'], None)
        self.assertIn('48.8155755', results[0]['boundingbox'])
        self.assertIn('48.902156', results[0]['boundingbox'])
        self.assertIn('2.224122', results[0]['boundingbox'])
        self.assertIn('2.4697602', results[0]['boundingbox'])

        json = """
        [
          {
            "place_id": "127732055",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://www.openstreetmap.org/copyright",
            "osm_type": "relation",
            "osm_id": "7444",
            "boundingbox": [
              "48.8155755",
              "48.902156",
              "2.224122",
              "2.4697602"
            ],
            "lat": "48.8565056",
            "lon": "2.3521334",
            "display_name": "This is the title",
            "class": "tourism",
            "type": "city",
            "importance": 0.96893459932191,
            "icon": "https://nominatim.openstreetmap.org/images/mapicons/poi_place_city.p.20.png",
            "address": {
              "city": "Paris",
              "county": "Paris",
              "state": "Île-de-France",
              "country": "France",
              "country_code": "fr",
              "address29": "Address"
            },
            "geojson": {
              "type": "Polygon",
              "coordinates": [
                [
                  [
                    2.224122,
                    48.854199
                  ]
                ]
              ]
            }
          },
          {
            "place_id": "127732055",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://www.openstreetmap.org/copyright",
            "osm_type": "relation",
            "osm_id": "7444",
            "boundingbox": [
              "48.8155755",
              "48.902156",
              "2.224122",
              "2.4697602"
            ],
            "lat": "48.8565056",
            "lon": "2.3521334",
            "display_name": "This is the title",
            "class": "tourism",
            "type": "city",
            "importance": 0.96893459932191,
            "icon": "https://nominatim.openstreetmap.org/images/mapicons/poi_place_city.p.20.png",
            "address": {
              "city": "Paris",
              "county": "Paris",
              "state": "Île-de-France",
              "country": "France",
              "postcode": 75000,
              "country_code": "fr"
            },
            "geojson": {
              "type": "Polygon",
              "coordinates": [
                [
                  [
                    2.224122,
                    48.854199
                  ]
                ]
              ]
            }
          },
          {
            "place_id": "127732055",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://www.openstreetmap.org/copyright",
            "osm_type": "node",
            "osm_id": "7444",
            "boundingbox": [
              "48.8155755",
              "48.902156",
              "2.224122",
              "2.4697602"
            ],
            "lat": "48.8565056",
            "lon": "2.3521334",
            "display_name": "This is the title",
            "class": "tourism",
            "type": "city",
            "importance": 0.96893459932191,
            "icon": "https://nominatim.openstreetmap.org/images/mapicons/poi_place_city.p.20.png",
            "address": {
              "city": "Paris",
              "county": "Paris",
              "state": "Île-de-France",
              "country": "France",
              "country_code": "fr",
              "address29": "Address"
            }
          }
        ]
        """
        response = mock.Mock(text=json)
        results = openstreetmap.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 3)
        self.assertIn('48.8565056', results[2]['geojson']['coordinates'])
        self.assertIn('2.3521334', results[2]['geojson']['coordinates'])
