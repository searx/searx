# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
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

        text = """
[{"Id":770931,
  "Episode":"S06E18",
  "Timestamp":534616,
  "Filename":""},
 {"Id":1657080,
  "Episode":"S12E14",
  "Timestamp":910868,
  "Filename":""},
 {"Id":1943753,
  "Episode":"S14E21",
  "Timestamp":773439,
  "Filename":""},
 {"Id":107835,
  "Episode":"S02E03",
  "Timestamp":531709,
  "Filename":""}]
        """

        response = mock.Mock(text=text)
        results = frinkiac.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]['title'], u'S06E18')
        self.assertIn('p=caption', results[0]['url'])
        self.assertIn('e=S06E18', results[0]['url'])
        self.assertIn('t=534616', results[0]['url'])
        self.assertEqual(results[0]['thumbnail_src'], 'https://frinkiac.com/img/S06E18/534616/medium.jpg')
        self.assertEqual(results[0]['img_src'], 'https://frinkiac.com/img/S06E18/534616.jpg')
