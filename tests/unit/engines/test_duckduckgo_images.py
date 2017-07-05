# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import duckduckgo_images
from searx.testing import SearxTestCase


class TestDuckduckgoImagesEngine(SearxTestCase):

    def test_request(self):
        duckduckgo_images.supported_languages = ['de-CH', 'en-US']

        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['is_test'] = True
        dicto['pageno'] = 1
        dicto['safesearch'] = 0
        dicto['language'] = 'all'
        params = duckduckgo_images.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('duckduckgo.com', params['url'])
        self.assertIn('s=0', params['url'])
        self.assertIn('p=-1', params['url'])
        self.assertIn('vqd=12345', params['url'])

        # test paging, safe search and language
        dicto['pageno'] = 2
        dicto['safesearch'] = 2
        dicto['language'] = 'de'
        params = duckduckgo_images.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('s=50', params['url'])
        self.assertIn('p=1', params['url'])
        self.assertIn('ch-de', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, duckduckgo_images.response, None)
        self.assertRaises(AttributeError, duckduckgo_images.response, [])
        self.assertRaises(AttributeError, duckduckgo_images.response, '')
        self.assertRaises(AttributeError, duckduckgo_images.response, '[]')

        response = mock.Mock(text='If this error persists, please let us know: ops@duckduckgo.com')
        self.assertEqual(duckduckgo_images.response(response), [])

        json = u"""
        {
            "query": "test_query",
            "results": [
                {
                    "title": "Result 1",
                    "url": "https://site1.url",
                    "thumbnail": "https://thumb1.nail",
                    "image": "https://image1"
                },
                {
                    "title": "Result 2",
                    "url": "https://site2.url",
                    "thumbnail": "https://thumb2.nail",
                    "image": "https://image2"
                }
            ]
        }
        """
        response = mock.Mock(text=json)
        results = duckduckgo_images.response(response)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Result 1')
        self.assertEqual(results[0]['url'], 'https://site1.url')
        self.assertEqual(results[0]['thumbnail_src'], 'https://thumb1.nail')
        self.assertEqual(results[0]['img_src'], 'https://image1')
        self.assertEqual(results[1]['title'], 'Result 2')
        self.assertEqual(results[1]['url'], 'https://site2.url')
        self.assertEqual(results[1]['thumbnail_src'], 'https://thumb2.nail')
        self.assertEqual(results[1]['img_src'], 'https://image2')
