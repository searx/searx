# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from requests import Request
from searx.engines import wolframalpha_noapi
from searx.testing import SearxTestCase


class TestWolframAlphaNoAPIEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        params = wolframalpha_noapi.request(query, dicto)

        self.assertIn('url', params)
        self.assertIn('https://www.wolframalpha.com/input/json.jsp', params['url'])
        self.assertIn(query, params['url'])
        self.assertEqual('https://www.wolframalpha.com/input/?i=test_query', params['headers']['Referer'])

    def test_response(self):
        self.assertRaises(AttributeError, wolframalpha_noapi.response, None)
        self.assertRaises(AttributeError, wolframalpha_noapi.response, [])
        self.assertRaises(AttributeError, wolframalpha_noapi.response, '')
        self.assertRaises(AttributeError, wolframalpha_noapi.response, '[]')

        referer_url = 'referer_url'
        request = Request(headers={'Referer': referer_url})

        # test failure
        json = r'''
        {"queryresult" : {
            "success" : false,
            "error" : false,
            "numpods" : 0,
            "id" : "",
            "host" : "https:\/\/www5a.wolframalpha.com",
            "didyoumeans" : {}
        }}
        '''
        response = mock.Mock(text=json, request=request)
        self.assertEqual(wolframalpha_noapi.response(response), [])

        # test basic case
        json = r'''
        {"queryresult" : {
            "success" : true,
            "error" : false,
            "numpods" : 6,
            "datatypes" : "Math",
            "id" : "queryresult_id",
            "host" : "https:\/\/www5b.wolframalpha.com",
            "related" : "related_url",
            "version" : "2.6",
            "pods" : [
                {
                    "title" : "Input",
                    "scanners" : [
                        "Identity"
                    ],
                    "id" : "Input",
                    "error" : false,
                    "numsubpods" : 1,
                    "subpods" : [
                        {
                            "title" : "",
                            "img" : {
                                "src" : "input_img_src.gif",
                                "alt" : "input_img_alt",
                                "title" : "input_img_title"
                            },
                            "plaintext" : "input_plaintext",
                            "minput" : "input_minput"
                        }
                    ]
                },
                {
                    "title" : "Result",
                    "scanners" : [
                        "Simplification"
                    ],
                    "id" : "Result",
                    "error" : false,
                    "numsubpods" : 1,
                    "primary" : true,
                    "subpods" : [
                        {
                            "title" : "",
                            "img" : {
                                "src" : "result_img_src.gif",
                                "alt" : "result_img_alt",
                                "title" : "result_img_title"
                            },
                            "plaintext" : "result_plaintext",
                            "moutput" : "result_moutput"
                        }
                    ]
                },
                {
                    "title" : "Manipulatives illustration",
                    "scanners" : [
                        "Arithmetic"
                    ],
                    "id" : "Illustration",
                    "error" : false,
                    "numsubpods" : 1,
                    "subpods" : [
                        {
                            "title" : "",
                            "CDFcontent" : "Resizeable",
                            "img" : {
                                "src" : "illustration_img_src.gif",
                                "alt" : "illustration_img_alt",
                                "title" : "illustration_img_title"
                            },
                            "plaintext" : "illustration_img_plaintext"
                        }
                    ]
                }
            ]
        }}
        '''
        response = mock.Mock(text=json, request=request)
        results = wolframalpha_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual('input_plaintext', results[0]['infobox'])

        self.assertEqual(len(results[0]['attributes']), 3)
        self.assertEqual('Input', results[0]['attributes'][0]['label'])
        self.assertEqual('input_plaintext', results[0]['attributes'][0]['value'])
        self.assertEqual('Result', results[0]['attributes'][1]['label'])
        self.assertEqual('result_plaintext', results[0]['attributes'][1]['value'])
        self.assertEqual('Manipulatives illustration', results[0]['attributes'][2]['label'])
        self.assertEqual('illustration_img_src.gif', results[0]['attributes'][2]['image']['src'])
        self.assertEqual('illustration_img_alt', results[0]['attributes'][2]['image']['alt'])

        self.assertEqual(len(results[0]['urls']), 1)

        self.assertEqual(referer_url, results[0]['urls'][0]['url'])
        self.assertEqual('Wolfram|Alpha', results[0]['urls'][0]['title'])
        self.assertEqual(referer_url, results[1]['url'])
        self.assertEqual('Wolfram|Alpha (input_plaintext)', results[1]['title'])
        self.assertIn('result_plaintext', results[1]['content'])

        # test calc
        json = r"""
        {"queryresult" : {
            "success" : true,
            "error" : false,
            "numpods" : 2,
            "datatypes" : "",
            "id" : "queryresult_id",
            "host" : "https:\/\/www4b.wolframalpha.com",
            "related" : "related_url",
            "version" : "2.6",
            "pods" : [
                {
                    "title" : "Indefinite integral",
                    "scanners" : [
                        "Integral"
                    ],
                    "id" : "IndefiniteIntegral",
                    "error" : false,
                    "numsubpods" : 1,
                    "primary" : true,
                    "subpods" : [
                        {
                            "title" : "",
                            "img" : {
                                "src" : "integral_img_src.gif",
                                "alt" : "integral_img_alt",
                                "title" : "integral_img_title"
                            },
                            "plaintext" : "integral_plaintext",
                            "minput" : "integral_minput",
                            "moutput" : "integral_moutput"
                        }
                    ]
                },
                {
                    "title" : "Plot of the integral",
                    "scanners" : [
                        "Integral"
                    ],
                    "id" : "Plot",
                    "error" : false,
                    "numsubpods" : 1,
                    "subpods" : [
                        {
                            "title" : "",
                            "img" : {
                                "src" : "plot.gif",
                                "alt" : "plot_alt",
                                "title" : "plot_title"
                            },
                            "plaintext" : "",
                            "minput" : "plot_minput"
                        }
                    ]
                }
            ]
        }}
        """
        response = mock.Mock(text=json, request=request)
        results = wolframalpha_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual('integral_plaintext', results[0]['infobox'])

        self.assertEqual(len(results[0]['attributes']), 2)
        self.assertEqual('Indefinite integral', results[0]['attributes'][0]['label'])
        self.assertEqual('integral_plaintext', results[0]['attributes'][0]['value'])
        self.assertEqual('Plot of the integral', results[0]['attributes'][1]['label'])
        self.assertEqual('plot.gif', results[0]['attributes'][1]['image']['src'])
        self.assertEqual('plot_alt', results[0]['attributes'][1]['image']['alt'])

        self.assertEqual(len(results[0]['urls']), 1)

        self.assertEqual(referer_url, results[0]['urls'][0]['url'])
        self.assertEqual('Wolfram|Alpha', results[0]['urls'][0]['title'])
        self.assertEqual(referer_url, results[1]['url'])
        self.assertEqual('Wolfram|Alpha (integral_plaintext)', results[1]['title'])
        self.assertIn('integral_plaintext', results[1]['content'])
