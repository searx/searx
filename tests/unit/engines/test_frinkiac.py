# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from json import dumps
from searx.engines import frinkiac
from searx.testing import SearxTestCase


class TestFrinkiacEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        request_dict = defaultdict(dict)
        params = frinkiac.request(query, request_dict)
        self.assertTrue('url' in params)

    def test_response(self):
        self.assertRaises(AttributeError, frinkiac.response, None)
        self.assertRaises(AttributeError, frinkiac.response, [])
        self.assertRaises(AttributeError, frinkiac.response, '')
        self.assertRaises(AttributeError, frinkiac.response, '[]')

        text = dumps([{'Id': 654234,
                       'Episode': 'S05E21',
                       'Timestamp': 3453455,
                       'Filename': ''},
                       {'Id': 435354,
                       'Episode': 'S05E22',
                       'Timestamp': 3453456,
                       'Filename': ''},
                       {'Id': 435333,
                       'Episode': 'S05E23',
                       'Timestamp': 3453457,
                       'Filename': ''},
                       {'Id': 477234,
                       'Episode': 'S05E24',
                       'Timestamp': 3453458,
                       'Filename': ''}])

        response = mock.Mock(text=text)
        results = frinkiac.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]['title'], u'S05E21')
        self.assertEqual(results[0]['url'], 'https://frinkiac.com/?p=caption&e=S05E21&t=3453455')
        self.assertEqual(results[0]['thumbnail_src'], 'https://frinkiac.com/img/S05E21/3453455/medium.jpg')
        self.assertEqual(results[0]['img_src'], 'https://frinkiac.com/img/S05E21/3453455.jpg')
