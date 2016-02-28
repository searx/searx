# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from requests import Request
from searx.engines import wolframalpha_api
from searx.testing import SearxTestCase


class TestWolframAlphaAPIEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        params = wolframalpha_api.request(query, dicto)

        # TODO: test api_key
        self.assertIn('url', params)
        self.assertIn('https://api.wolframalpha.com/v2/query?', params['url'])
        self.assertIn(query, params['url'])
        self.assertEqual('https://www.wolframalpha.com/input/?i=test_query', params['headers']['Referer'])

    def test_replace_pua_chars(self):
        self.assertEqual('i', wolframalpha_api.replace_pua_chars(u'\uf74e'))

    def test_response(self):
        self.assertRaises(AttributeError, wolframalpha_api.response, None)
        self.assertRaises(AttributeError, wolframalpha_api.response, [])
        self.assertRaises(AttributeError, wolframalpha_api.response, '')
        self.assertRaises(AttributeError, wolframalpha_api.response, '[]')

        referer_url = 'referer_url'
        request = Request(headers={'Referer': referer_url})

        # test failure
        xml = '''<?xml version='1.0' encoding='UTF-8'?>
        <queryresult success='false' error='false' />
        '''
        response = mock.Mock(content=xml)
        self.assertEqual(wolframalpha_api.response(response), [])

        # test basic case
        xml = """<?xml version='1.0' encoding='UTF-8'?>
        <queryresult success='true'
            error='false'
            numpods='3'
            datatypes='Math'
            id='queryresult_id'
            host='http://www4c.wolframalpha.com'
            related='related_url'
            version='2.6'>
            <pod title='Input'
                 scanner='Identity'
                 id='Input'
                 numsubpods='1'>
                  <subpod title=''>
                       <img src='input_img_src.gif'
                           alt='input_img_alt'
                           title='input_img_title' />
                       <plaintext>input_plaintext</plaintext>
                  </subpod>
             </pod>
             <pod title='Result'
                 scanner='Simplification'
                 id='Result'
                 numsubpods='1'
                 primary='true'>
                  <subpod title=''>
                       <img src='result_img_src.gif'
                           alt='result_img_alt'
                           title='result_img_title' />
                       <plaintext>result_plaintext</plaintext>
                  </subpod>
             </pod>
             <pod title='Manipulatives illustration'
                 scanner='Arithmetic'
                 id='Illustration'
                 numsubpods='1'>
                  <subpod title=''>
                       <img src='illustration_img_src.gif'
                           alt='illustration_img_alt' />
                       <plaintext>illustration_plaintext</plaintext>
                  </subpod>
             </pod>
        </queryresult>
        """
        response = mock.Mock(content=xml, request=request)
        results = wolframalpha_api.response(response)
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
        xml = """<?xml version='1.0' encoding='UTF-8'?>
        <queryresult success='true'
            error='false'
            numpods='2'
            datatypes=''
            parsetimedout='false'
            id='queryresult_id'
            host='http://www5b.wolframalpha.com'
            related='related_url'
            version='2.6' >
            <pod title='Indefinite integral'
                scanner='Integral'
                id='IndefiniteIntegral'
                error='false'
                numsubpods='1'
                primary='true'>
                <subpod title=''>
                    <img src='integral_image.gif'
                        alt='integral_img_alt'
                        title='integral_img_title' />
                    <plaintext>integral_plaintext</plaintext>
                </subpod>
            </pod>
            <pod title='Plot'
                scanner='Plotter'
                id='Plot'
                error='false'
                numsubpods='1'>
                <subpod title=''>
                    <img src='plot.gif'
                        alt='plot_alt'
                        title='' />
                    <plaintext></plaintext>
                </subpod>
            </pod>
        </queryresult>
        """
        response = mock.Mock(content=xml, request=request)
        results = wolframalpha_api.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertIn('integral_plaintext', results[0]['infobox'])

        self.assertEqual(len(results[0]['attributes']), 2)
        self.assertIn('Indefinite integral', results[0]['attributes'][0]['label'])
        self.assertIn('integral_plaintext', results[0]['attributes'][0]['value'])
        self.assertIn('Plot', results[0]['attributes'][1]['label'])
        self.assertIn('plot.gif', results[0]['attributes'][1]['image']['src'])
        self.assertIn('plot_alt', results[0]['attributes'][1]['image']['alt'])

        self.assertEqual(len(results[0]['urls']), 1)

        self.assertEqual(referer_url, results[0]['urls'][0]['url'])
        self.assertEqual('Wolfram|Alpha', results[0]['urls'][0]['title'])
        self.assertEqual(referer_url, results[1]['url'])
        self.assertEqual('Wolfram|Alpha', results[1]['title'])
