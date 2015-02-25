# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import photon
from searx.testing import SearxTestCase


class TestPhotonEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'all'
        params = photon.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('photon.komoot.de', params['url'])

        dicto['language'] = 'all'
        params = photon.request(query, dicto)
        self.assertNotIn('lang', params['url'])

        dicto['language'] = 'al'
        params = photon.request(query, dicto)
        self.assertNotIn('lang', params['url'])

        dicto['language'] = 'fr'
        params = photon.request(query, dicto)
        self.assertIn('fr', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, photon.response, None)
        self.assertRaises(AttributeError, photon.response, [])
        self.assertRaises(AttributeError, photon.response, '')
        self.assertRaises(AttributeError, photon.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(photon.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(photon.response(response), [])

        json = """
        {
          "features": [
            {
              "properties": {
                "osm_key": "waterway",
                "extent": [
                  -1.4508446,
                  51.1614997,
                  -1.4408036,
                  51.1525635
                ],
                "name": "This is the title",
                "state": "England",
                "osm_id": 114823817,
                "osm_type": "W",
                "osm_value": "river",
                "city": "Test Valley",
                "country": "United Kingdom"
              },
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [
                  -1.4458571,
                  51.1576661
                ]
              }
            },
            {
              "properties": {
                "osm_key": "place",
                "street": "Rue",
                "state": "Ile-de-France",
                "osm_id": 129211377,
                "osm_type": "R",
                "housenumber": "10",
                "postcode": "75011",
                "osm_value": "house",
                "city": "Paris",
                "country": "France"
              },
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [
                  2.3725025,
                  48.8654481
                ]
              }
            },
            {
              "properties": {
                "osm_key": "amenity",
                "street": "Allée",
                "name": "Bibliothèque",
                "state": "Ile-de-France",
                "osm_id": 1028573132,
                "osm_type": "N",
                "postcode": "75001",
                "osm_value": "library",
                "city": "Paris",
                "country": "France"
              },
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [
                  2.3445634,
                  48.862494
                ]
              }
            },
            {
              "properties": {
                "osm_key": "amenity",
                "osm_id": 1028573132,
                "osm_type": "Y",
                "postcode": "75001",
                "osm_value": "library",
                "city": "Paris",
                "country": "France"
              },
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [
                  2.3445634,
                  48.862494
                ]
              }
            },
            {
            }
        ],
          "type": "FeatureCollection"
        }
        """
        response = mock.Mock(text=json)
        results = photon.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['content'], '')
        self.assertEqual(results[0]['longitude'], -1.4458571)
        self.assertEqual(results[0]['latitude'], 51.1576661)
        self.assertIn(-1.4508446, results[0]['boundingbox'])
        self.assertIn(51.1614997, results[0]['boundingbox'])
        self.assertIn(-1.4408036, results[0]['boundingbox'])
        self.assertIn(51.1525635, results[0]['boundingbox'])
        self.assertIn('type', results[0]['geojson'])
        self.assertEqual(results[0]['geojson']['type'], 'Point')
        self.assertEqual(results[0]['address'], None)
        self.assertEqual(results[0]['osm']['type'], 'way')
        self.assertEqual(results[0]['osm']['id'], 114823817)
        self.assertEqual(results[0]['url'], 'https://openstreetmap.org/way/114823817')
        self.assertEqual(results[1]['osm']['type'], 'relation')
        self.assertEqual(results[2]['address']['name'], u'Bibliothèque')
        self.assertEqual(results[2]['address']['house_number'], None)
        self.assertEqual(results[2]['address']['locality'], 'Paris')
        self.assertEqual(results[2]['address']['postcode'], '75001')
        self.assertEqual(results[2]['address']['country'], 'France')
        self.assertEqual(results[2]['osm']['type'], 'node')
