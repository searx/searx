# -*- coding: utf-8 -*-
from collections import defaultdict
from searx.engines import wolframalpha_noapi
from searx.testing import SearxTestCase


class TestWolframAlphaNoAPIEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = wolframalpha_noapi.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('wolframalpha.com', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, wolframalpha_noapi.response, None)
        self.assertRaises(AttributeError, wolframalpha_noapi.response, [])
        self.assertRaises(AttributeError, wolframalpha_noapi.response, '')
        self.assertRaises(AttributeError, wolframalpha_noapi.response, '[]')
        # TODO
