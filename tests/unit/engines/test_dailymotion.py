from collections import defaultdict
import mock
from searx.engines import dailymotion
from searx.testing import SearxTestCase


class TestDailymotionEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['language'] = 'fr_FR'
        params = dailymotion.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('dailymotion.com' in params['url'])
        self.assertTrue('fr' in params['url'])

        dicto['language'] = 'all'
        params = dailymotion.request(query, dicto)
        self.assertTrue('en' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, dailymotion.response, None)
        self.assertRaises(AttributeError, dailymotion.response, [])
        self.assertRaises(AttributeError, dailymotion.response, '')
        self.assertRaises(AttributeError, dailymotion.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(dailymotion.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(dailymotion.response(response), [])

        json = """
        {
        "page": 1,
        "limit": 5,
        "explicit": false,
        "total": 289487,
        "has_more": true,
        "list": [
            {
            "created_time": 1422173451,
            "title": "Title",
            "description": "Description",
            "duration": 81,
            "url": "http://www.url",
            "thumbnail_360_url": "http://thumbnail",
            "id": "x2fit7q"
            }
        ]
        }
        """
        response = mock.Mock(text=json)
        results = dailymotion.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'http://www.url')
        self.assertEqual(results[0]['content'], 'Description')
        self.assertIn('x2fit7q', results[0]['embedded'])

        json = r"""
        {"toto":[
            {"id":200,"name":"Artist Name",
            "link":"http:\/\/www.dailymotion.com\/artist\/1217","type":"artist"}
        ]}
        """
        response = mock.Mock(text=json)
        results = dailymotion.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
