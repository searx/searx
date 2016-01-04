# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
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

        html = """
        <!DOCTYPE html>
            <title> Parangaricutirimícuaro - Wolfram|Alpha</title>
            <meta charset="utf-8" />
            <body>
                <div id="closest">
                    <p class="pfail">Wolfram|Alpha doesn't know how to interpret your input.</p>
                    <div id="dtips">
                        <div class="tip">
                            <span class="tip-title">Tip:&nbsp;</span>
                                Check your spelling, and use English
                            <span class="tip-extra"></span>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
        # test failed query
        response = mock.Mock(text=html)
        self.assertEqual(wolframalpha_noapi.response(response), [])

        html = """
        <!DOCTYPE html>
            <title> sqrt(-1) - Wolfram|Alpha</title>
            <meta charset="utf-8" />
            <body>
                <script type="text/javascript">
                  try {
                    if (typeof context.jsonArray.popups.pod_0100 == "undefined" ) {
                      context.jsonArray.popups.pod_0100 = [];
                    }
                    context.jsonArray.popups.pod_0100.push( {"stringified": "sqrt(-1)","mInput": "","mOutput": ""});
                  } catch(e) { }

                  try {
                    if (typeof context.jsonArray.popups.pod_0200 == "undefined" ) {
                      context.jsonArray.popups.pod_0200 = [];
                    }
                    context.jsonArray.popups.pod_0200.push( {"stringified": "i","mInput": "","mOutput": ""});
                  } catch(e) { }
                </script>
            </body>
        </html>
        """
        # test plaintext
        response = mock.Mock(text=html)
        results = wolframalpha_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEquals('i', results[0]['answer'])
        self.assertIn('sqrt(-1) - Wolfram|Alpha', results[1]['title'])
        self.assertEquals('http://www.wolframalpha.com/input/?i=+sqrt%28-1%29', results[1]['url'])

        html = """
        <!DOCTYPE html>
            <title> integral 1/x - Wolfram|Alpha</title>
            <meta charset="utf-8" />
            <body>
                <script type="text/javascript">
                  try {
                    if (typeof context.jsonArray.popups.pod_0100 == "undefined" ) {
                      context.jsonArray.popups.pod_0100 = [];
                    }
                    context.jsonArray.popups.pod_0100.push( {"stringified": "integral 1\/x dx = log(x)+constant"});
                  } catch(e) { }
                </script>
            </body>
        </html>
        """
        # test integral
        response = mock.Mock(text=html)
        results = wolframalpha_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertIn('log(x)+c', results[0]['answer'])
        self.assertIn('integral 1/x - Wolfram|Alpha', results[1]['title'])
        self.assertEquals('http://www.wolframalpha.com/input/?i=+integral+1%2Fx', results[1]['url'])

        html = """
        <!DOCTYPE html>
            <title> &int;1&#x2f;x &#xf74c;x - Wolfram|Alpha</title>
            <meta charset="utf-8" />
            <body>
                <script type="text/javascript">
                  try {
                    if (typeof context.jsonArray.popups.pod_0100 == "undefined" ) {
                      context.jsonArray.popups.pod_0100 = [];
                    }
                    context.jsonArray.popups.pod_0100.push( {"stringified": "integral 1\/x dx = log(x)+constant"});
                  } catch(e) { }
                </script>
            </body>
        </html>
        """
        # test input in mathematical notation
        response = mock.Mock(text=html)
        results = wolframalpha_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertIn('log(x)+c', results[0]['answer'])
        self.assertIn('∫1/x x - Wolfram|Alpha'.decode('utf-8'), results[1]['title'])
        self.assertEquals('http://www.wolframalpha.com/input/?i=+%E2%88%AB1%2Fx+%EF%9D%8Cx', results[1]['url'])

        html = """
        <!DOCTYPE html>
            <title> 1 euro to yen - Wolfram|Alpha</title>
            <meta charset="utf-8" />
            <body>
                <script type="text/javascript">
                  try {
                    if (typeof context.jsonArray.popups.pod_0100 == "undefined" ) {
                      context.jsonArray.popups.pod_0100 = [];
                    }
                  context.jsonArray.popups.pod_0100.push( {"stringified": "convert euro1  (euro) to Japanese yen"});
                  } catch(e) { }

                  try {
                    if (typeof context.jsonArray.popups.pod_0200 == "undefined" ) {
                      context.jsonArray.popups.pod_0200 = [];
                    }
                    context.jsonArray.popups.pod_0200.push( {"stringified": "&yen;130.5  (Japanese yen)"});
                  } catch(e) { }
                </script>
            </body>
        </html>
        """
        # test output in htmlentity
        response = mock.Mock(text=html)
        results = wolframalpha_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertIn("¥".decode('utf-8'), results[0]['answer'])
        self.assertIn('1 euro to yen - Wolfram|Alpha', results[1]['title'])
        self.assertEquals('http://www.wolframalpha.com/input/?i=+1+euro+to+yen', results[1]['url'])
