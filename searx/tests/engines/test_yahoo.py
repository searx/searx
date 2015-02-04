# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import yahoo
from searx.testing import SearxTestCase


class TestYahooEngine(SearxTestCase):

    def test_parse_url(self):
        test_url = 'http://r.search.yahoo.com/_ylt=A0LEb9JUSKcAEGRXNyoA;_ylu=X3oDMTEzZm1qazYwBHNlYwNzcgRwb3MDMQRjb' +\
                   '2xvA2Jm2dGlkA1NNRTcwM18x/RV=2/RE=1423106085/RO=10/RU=https%3a%2f%2fthis.is.the.url%2f/RK=0/RS=' +\
                   'dtcJsfP4mEeBOjnVfUQ-'
        url = yahoo.parse_url(test_url)
        self.assertEqual('https://this.is.the.url/', url)

        test_url = 'http://r.search.yahoo.com/_ylt=A0LElb9JUSKcAEGRXNyoA;_ylu=X3oDMTEzZm1qazYwBHNlYwNzcgRwb3MDMQRjb' +\
                   '2xvA2Jm2dGlkA1NNRTcwM18x/RV=2/RE=1423106085/RO=10/RU=https%3a%2f%2fthis.is.the.url%2f/RS=' +\
                   'dtcJsfP4mEeBOjnVfUQ-'
        url = yahoo.parse_url(test_url)
        self.assertEqual('https://this.is.the.url/', url)

        test_url = 'https://this.is.the.url/'
        url = yahoo.parse_url(test_url)
        self.assertEqual('https://this.is.the.url/', url)

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        params = yahoo.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('search.yahoo.com', params['url'])
        self.assertIn('fr', params['url'])
        self.assertIn('cookies', params)
        self.assertIn('sB', params['cookies'])
        self.assertIn('fr', params['cookies']['sB'])

        dicto['language'] = 'all'
        params = yahoo.request(query, dicto)
        self.assertIn('cookies', params)
        self.assertIn('sB', params['cookies'])
        self.assertIn('en', params['cookies']['sB'])
        self.assertIn('en', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, yahoo.response, None)
        self.assertRaises(AttributeError, yahoo.response, [])
        self.assertRaises(AttributeError, yahoo.response, '')
        self.assertRaises(AttributeError, yahoo.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(yahoo.response(response), [])

        html = """
        <div class="res">
            <div>
                <h3>
                <a id="link-1" class="yschttl spt" href="http://r.search.yahoo.com/_ylt=A0LEVzClb9JUSKcAEGRXNyoA;
                    _ylu=X3oDMTEzZm1qazYwBHNlYwNzcgRwb3MDMQRjb2xvA2JmMQR2dGlkA1NNRTcwM18x/RV=2/RE=1423106085/RO=10
                    /RU=https%3a%2f%2fthis.is.the.url%2f/RK=0/RS=dtcJsfP4mEeBOjnVfUQ-"target="_blank" data-bk="5063.1">
                    <b>This</b> is the title
                </a>
                </h3>
            </div>
            <span class="url" dir="ltr">www.<b>test</b>.com</span>
            <div class="abstr">
                <b>This</b> is the content
            </div>
        </div>
        <div id="satat"  data-bns="Yahoo" data-bk="124.1">
            <h2>Also Try</h2>
            <table>
                <tbody>
                    <tr>
                        <td>
                            <a id="srpnat0" class="" href="https://search.yahoo.com/search=rs-bottom" >
                                <span>
                                    <b></b>This is <b>the suggestion</b>
                                </span>
                            </a>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        response = mock.Mock(text=html)
        results = yahoo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://this.is.the.url/')
        self.assertEqual(results[0]['content'], 'This is the content')
        self.assertEqual(results[1]['suggestion'], 'This is the suggestion')

        html = """
        <div class="res">
            <div>
                <h3>
                <a id="link-1" class="yschttl spt" href="http://r.search.yahoo.com/_ylt=A0LEVzClb9JUSKcAEGRXNyoA;
                    _ylu=X3oDMTEzZm1qazYwBHNlYwNzcgRwb3MDMQRjb2xvA2JmMQR2dGlkA1NNRTcwM18x/RV=2/RE=1423106085/RO=10
                    /RU=https%3a%2f%2fthis.is.the.url%2f/RK=0/RS=dtcJsfP4mEeBOjnVfUQ-"target="_blank" data-bk="5063.1">
                    <b>This</b> is the title
                </a>
                </h3>
            </div>
            <span class="url" dir="ltr">www.<b>test</b>.com</span>
            <div class="abstr">
                <b>This</b> is the content
            </div>
        </div>
        <div class="res">
            <div>
                <h3>
                <a id="link-1" class="yschttl spt">
                    <b>This</b> is the title
                </a>
                </h3>
            </div>
            <span class="url" dir="ltr">www.<b>test</b>.com</span>
            <div class="abstr">
                <b>This</b> is the content
            </div>
        </div>
        <div class="res">
            <div>
                <h3>
                </h3>
            </div>
            <span class="url" dir="ltr">www.<b>test</b>.com</span>
            <div class="abstr">
                <b>This</b> is the content
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = yahoo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://this.is.the.url/')
        self.assertEqual(results[0]['content'], 'This is the content')

        html = """
        <li class="b_algo" u="0|5109|4755453613245655|UAGjXgIrPH5yh-o5oNHRx_3Zta87f_QO">
        </li>
        """
        response = mock.Mock(text=html)
        results = yahoo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
