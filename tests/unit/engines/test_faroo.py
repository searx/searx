# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import faroo
from searx.testing import SearxTestCase


class TestFarooEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        dicto['category'] = 'general'
        params = faroo.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('faroo.com', params['url'])
        self.assertIn('en', params['url'])
        self.assertIn('web', params['url'])

        dicto['language'] = 'all'
        params = faroo.request(query, dicto)
        self.assertIn('en', params['url'])

        dicto['language'] = 'de_DE'
        params = faroo.request(query, dicto)
        self.assertIn('de', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, faroo.response, None)
        self.assertRaises(AttributeError, faroo.response, [])
        self.assertRaises(AttributeError, faroo.response, '')
        self.assertRaises(AttributeError, faroo.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(faroo.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(faroo.response(response), [])

        response = mock.Mock(text='{"data": []}', status_code=429)
        self.assertRaises(Exception, faroo.response, response)

        json = """
        {
          "results": [
            {
              "title": "This is the title",
              "kwic": "This is the content",
              "content": "",
              "url": "http://this.is.the.url/",
              "iurl": "",
              "domain": "css3test.com",
              "author": "Jim Dalrymple",
              "news": true,
              "votes": "10",
              "date": 1360622563000,
              "related": []
            },
            {
              "title": "This is the title2",
              "kwic": "This is the content2",
              "content": "",
              "url": "http://this.is.the.url2/",
              "iurl": "",
              "domain": "css3test.com",
              "author": "Jim Dalrymple",
              "news": false,
              "votes": "10",
              "related": []
            },
            {
              "title": "This is the title3",
              "kwic": "This is the content3",
              "content": "",
              "url": "http://this.is.the.url3/",
              "iurl": "http://upload.wikimedia.org/optimized.jpg",
              "domain": "css3test.com",
              "author": "Jim Dalrymple",
              "news": false,
              "votes": "10",
              "related": []
            }
          ],
          "query": "test",
          "suggestions": [],
          "count": 100,
          "start": 1,
          "length": 10,
          "time": "15"
        }
        """
        response = mock.Mock(text=json)
        results = faroo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url/')
        self.assertEqual(results[0]['content'], 'This is the content')
        self.assertEqual(results[1]['title'], 'This is the title2')
        self.assertEqual(results[1]['url'], 'http://this.is.the.url2/')
        self.assertEqual(results[1]['content'], 'This is the content2')
        self.assertEqual(results[2]['thumbnail'], 'http://upload.wikimedia.org/optimized.jpg')

        json = """
        {}
        """
        response = mock.Mock(text=json)
        results = faroo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
