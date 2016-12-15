# -*- coding: utf-8 -*-
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

    def test_fetch_supported_languages(self):
        json = r"""
        {"list":[{"code":"af","name":"Afrikaans","native_name":"Afrikaans",
                  "localized_name":"Afrikaans","display_name":"Afrikaans"},
                 {"code":"ar","name":"Arabic","native_name":"\u0627\u0644\u0639\u0631\u0628\u064a\u0629",
                  "localized_name":"Arabic","display_name":"Arabic"},
                 {"code":"la","name":"Latin","native_name":null,
                  "localized_name":"Latin","display_name":"Latin"}
        ]}
        """
        response = mock.Mock(text=json)
        languages = dailymotion._fetch_supported_languages(response)
        self.assertEqual(type(languages), dict)
        self.assertEqual(len(languages), 3)
        self.assertIn('af', languages)
        self.assertIn('ar', languages)
        self.assertIn('la', languages)

        self.assertEqual(type(languages['af']), dict)
        self.assertEqual(type(languages['ar']), dict)
        self.assertEqual(type(languages['la']), dict)

        self.assertIn('name', languages['af'])
        self.assertIn('name', languages['ar'])
        self.assertNotIn('name', languages['la'])

        self.assertIn('english_name', languages['af'])
        self.assertIn('english_name', languages['ar'])
        self.assertIn('english_name', languages['la'])

        self.assertEqual(languages['af']['name'], 'Afrikaans')
        self.assertEqual(languages['af']['english_name'], 'Afrikaans')
        self.assertEqual(languages['ar']['name'], u'العربية')
        self.assertEqual(languages['ar']['english_name'], 'Arabic')
        self.assertEqual(languages['la']['english_name'], 'Latin')
