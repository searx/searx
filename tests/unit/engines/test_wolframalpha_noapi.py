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
        json = '''
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
        json = '''
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
        self.assertIn('input_plaintext', results[0]['infobox'])

        self.assertEqual(len(results[0]['attributes']), 3)
        self.assertIn('Input', results[0]['attributes'][0]['label'])
        self.assertIn('input_plaintext', results[0]['attributes'][0]['value'])
        self.assertIn('Result', results[0]['attributes'][1]['label'])
        self.assertIn('result_plaintext', results[0]['attributes'][1]['value'])
        self.assertIn('Manipulatives illustration', results[0]['attributes'][2]['label'])
        self.assertIn('illustration_img_src.gif', results[0]['attributes'][2]['image']['src'])
        self.assertIn('illustration_img_alt', results[0]['attributes'][2]['image']['alt'])

        self.assertEqual(len(results[0]['urls']), 1)

        self.assertEqual(referer_url, results[0]['urls'][0]['url'])
        self.assertEqual('Wolfram|Alpha', results[0]['urls'][0]['title'])
        self.assertEqual(referer_url, results[1]['url'])
        self.assertEqual('Wolfram|Alpha', results[1]['title'])

        # test calc
        json = """
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
                    "numsubpods" : 0,
                    "async" : "invalid_async_url"
                }
            ]
        }}
        """
        response = mock.Mock(text=json, request=request)
        results = wolframalpha_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertIn('integral_plaintext', results[0]['infobox'])

        self.assertEqual(len(results[0]['attributes']), 1)
        self.assertIn('Indefinite integral', results[0]['attributes'][0]['label'])
        self.assertIn('integral_plaintext', results[0]['attributes'][0]['value'])

        self.assertEqual(len(results[0]['urls']), 1)

        self.assertEqual(referer_url, results[0]['urls'][0]['url'])
        self.assertEqual('Wolfram|Alpha', results[0]['urls'][0]['title'])
        self.assertEqual(referer_url, results[1]['url'])
        self.assertEqual('Wolfram|Alpha', results[1]['title'])

    def test_parse_async_pod(self):
        self.assertRaises(AttributeError, wolframalpha_noapi.parse_async_pod, None)
        self.assertRaises(AttributeError, wolframalpha_noapi.parse_async_pod, [])
        self.assertRaises(AttributeError, wolframalpha_noapi.parse_async_pod, '')
        self.assertRaises(AttributeError, wolframalpha_noapi.parse_async_pod, '[]')

        # test plot
        xml = '''<?xml version='1.0' encoding='UTF-8'?>
        <pod title='Plot'
            scanner='Plot'
            id='Plot'
            error='false'
            numsubpods='1'>
            <subpod title=''>
                <img src='plot_img_src.gif'
                    alt='plot_img_alt'
                    title='plot_img_title' />
                <plaintext>plot_plaintext</plaintext>
                <minput>plot_minput</minput>
            </subpod>
        </pod>
        '''
        response = mock.Mock(content=xml)
        pod = wolframalpha_noapi.parse_async_pod(response)
        self.assertEqual(len(pod['subpods']), 1)
        self.assertEqual('', pod['subpods'][0]['title'])
        self.assertEqual('plot_plaintext', pod['subpods'][0]['plaintext'])
        self.assertEqual('plot_img_src.gif', pod['subpods'][0]['img']['src'])
        self.assertEqual('plot_img_alt', pod['subpods'][0]['img']['alt'])
