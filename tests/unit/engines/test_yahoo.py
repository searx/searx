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
        dicto['time_range'] = ''
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

    def test_no_url_in_request_year_time_range(self):
        dicto = defaultdict(dict)
        query = 'test_query'
        dicto['time_range'] = 'year'
        params = yahoo.request(query, dicto)
        self.assertEqual({}, params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, yahoo.response, None)
        self.assertRaises(AttributeError, yahoo.response, [])
        self.assertRaises(AttributeError, yahoo.response, '')
        self.assertRaises(AttributeError, yahoo.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(yahoo.response(response), [])

        html = """
<ol class="reg mb-15 searchCenterMiddle">
    <li class="first">
        <div class="dd algo fst Sr">
            <div class="compTitle">
                <h3 class="title"><a class=" td-u" href="http://r.search.yahoo.com/_ylt=A0LEb9JUSKcAEGRXNyoA;
                     _ylu=X3oDMTEzZm1qazYwBHNlYwNzcgRwb3MDMQRjb2xvA2Jm2dGlkA1NNRTcwM18x/RV=2/RE=1423106085/RO=10
                     /RU=https%3a%2f%2fthis.is.the.url%2f/RK=0/RS=dtcJsfP4mEeBOjnVfUQ-"
                     target="_blank" data-bid="54e712e13671c">
                     <b><b>This is the title</b></b></a>
                </h3>
            </div>
            <div class="compText aAbs">
                <p class="lh-18"><b><b>This is the </b>content</b>
                </p>
            </div>
        </div>
    </li>
    <li>
        <div class="dd algo lst Sr">
            <div class="compTitle">
            </div>
            <div class="compText aAbs">
                <p class="lh-18">This is the second content</p>
            </div>
        </div>
    </li>
</ol>
<div class="dd assist fst lst AlsoTry" data-bid="54e712e138d04">
    <div class="compTitle mb-4 h-17">
        <h3 class="title">Also Try</h3> </div>
    <table class="compTable m-0 ac-1st td-u fz-ms">
        <tbody>
            <tr>
                <td class="w-50p pr-28"><a href="https://search.yahoo.com/"><B>This is the </B>suggestion<B></B></a>
                </td>
            </tr>
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
<ol class="reg mb-15 searchCenterMiddle">
    <li class="first">
        <div class="dd algo fst Sr">
            <div class="compTitle">
                <h3 class="title"><a class=" td-u" href="http://r.search.yahoo.com/_ylt=A0LEb9JUSKcAEGRXNyoA;
                     _ylu=X3oDMTEzZm1qazYwBHNlYwNzcgRwb3MDMQRjb2xvA2Jm2dGlkA1NNRTcwM18x/RV=2/RE=1423106085/RO=10
                     /RU=https%3a%2f%2fthis.is.the.url%2f/RK=0/RS=dtcJsfP4mEeBOjnVfUQ-"
                     target="_blank" data-bid="54e712e13671c">
                  <b><b>This is the title</b></b></a>
                </h3>
            </div>
            <div class="compText aAbs">
                <p class="lh-18"><b><b>This is the </b>content</b>
                </p>
            </div>
        </div>
    </li>
</ol>
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

    def test_fetch_supported_languages(self):
        html = """<html></html>"""
        response = mock.Mock(text=html)
        results = yahoo._fetch_supported_languages(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        html = """
        <html>
            <div>
                <div id="yschlang">
                    <span>
                        <label><input value="lang_ar"></input></label>
                    </span>
                    <span>
                        <label><input value="lang_zh_chs"></input></label>
                        <label><input value="lang_zh_cht"></input></label>
                    </span>
                </div>
            </div>
        </html>
        """
        response = mock.Mock(text=html)
        languages = yahoo._fetch_supported_languages(response)
        self.assertEqual(type(languages), list)
        self.assertEqual(len(languages), 3)
        self.assertIn('ar', languages)
        self.assertIn('zh-chs', languages)
        self.assertIn('zh-cht', languages)
