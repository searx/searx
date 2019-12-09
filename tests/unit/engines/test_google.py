# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
import lxml
from searx.engines import google
from searx.testing import SearxTestCase


class TestGoogleEngine(SearxTestCase):

    def mock_response(self, text):
        response = mock.Mock(text=text, url='https://www.google.com/search?q=test&start=0&gbv=1&gws_rd=cr')
        response.search_params = mock.Mock()
        response.search_params.get = mock.Mock(return_value='www.google.com')
        return response

    def test_request(self):
        google.supported_languages = ['en', 'fr', 'zh-CN', 'iw']
        google.language_aliases = {'he': 'iw'}

        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr-FR'
        dicto['time_range'] = ''
        params = google.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('google.fr', params['url'])
        self.assertIn('fr', params['url'])
        self.assertIn('fr', params['headers']['Accept-Language'])

        dicto['language'] = 'en-US'
        params = google.request(query, dicto)
        self.assertIn('google.com', params['url'])
        self.assertIn('en', params['url'])
        self.assertIn('en', params['headers']['Accept-Language'])

        dicto['language'] = 'zh'
        params = google.request(query, dicto)
        self.assertIn('google.com', params['url'])
        self.assertIn('zh-CN', params['url'])
        self.assertIn('zh-CN', params['headers']['Accept-Language'])

        dicto['language'] = 'he'
        params = google.request(query, dicto)
        self.assertIn('google.com', params['url'])
        self.assertIn('iw', params['url'])
        self.assertIn('iw', params['headers']['Accept-Language'])

    def test_response(self):
        self.assertRaises(AttributeError, google.response, None)
        self.assertRaises(AttributeError, google.response, [])
        self.assertRaises(AttributeError, google.response, '')
        self.assertRaises(AttributeError, google.response, '[]')

        response = self.mock_response('<html></html>')
        self.assertEqual(google.response(response), [])

        html = """
        <div class="ZINbbc xpd O9g5cc uUPGi">
            <div>
                <div class="kCrYT">
                    <a href="/url?q=http://this.should.be.the.link/">
                        <div class="BNeawe">
                            <b>This</b> is <b>the</b> title
                        </div>
                        <div class="BNeawe">
                            http://website
                        </div>
                    </a>
                </div>
                <div class="kCrYT">
                    <div>
                        <div class="BNeawe">
                            <div>
                                <div class="BNeawe">
                                    This should be the content.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </p>
        <div class="ZINbbc xpd O9g5cc uUPGi">
            <div>
                <div class="kCrYT">
                    <span>
                        <div class="BNeawe">
                            Related searches
                        </div>
                    </span>
                </div>
                <div class="rVLSBd">
                    <a>
                        <div>
                            <div class="BNeawe">
                                suggestion title
                            </div>
                        </div>
                    </a>
                </div>
            </div>
        </p>
        """
        response = self.mock_response(html)
        results = google.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'http://this.should.be.the.link/')
        self.assertEqual(results[0]['content'], 'This should be the content.')
        self.assertEqual(results[1]['suggestion'], 'suggestion title')

        html = """
        <li class="b_algo" u="0|5109|4755453613245655|UAGjXgIrPH5yh-o5oNHRx_3Zta87f_QO">
        </li>
        """
        response = self.mock_response(html)
        results = google.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        response = mock.Mock(text='<html></html>', url='https://sorry.google.com')
        response.search_params = mock.Mock()
        response.search_params.get = mock.Mock(return_value='www.google.com')
        self.assertRaises(RuntimeWarning, google.response, response)

        response = mock.Mock(text='<html></html>', url='https://www.google.com/sorry/IndexRedirect')
        response.search_params = mock.Mock()
        response.search_params.get = mock.Mock(return_value='www.google.com')
        self.assertRaises(RuntimeWarning, google.response, response)

    def test_parse_images(self):
        html = """
        <li>
            <div>
                <a href="http://www.google.com/url?q=http://this.is.the.url/">
                    <img style="margin:3px 0;margin-right:6px;padding:0" height="90"
                        src="https://this.is.the.image/image.jpg" width="60" align="middle" alt="" border="0">
                </a>
            </div>
        </li>
        """
        dom = lxml.html.fromstring(html)
        results = google.parse_images(dom, 'www.google.com')
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['url'], 'http://this.is.the.url/')
        self.assertEqual(results[0]['title'], '')
        self.assertEqual(results[0]['content'], '')
        self.assertEqual(results[0]['img_src'], 'https://this.is.the.image/image.jpg')

    def test_fetch_supported_languages(self):
        html = """<html></html>"""
        response = mock.Mock(text=html)
        languages = google._fetch_supported_languages(response)
        self.assertEqual(type(languages), dict)
        self.assertEqual(len(languages), 0)

        html = u"""
        <html>
            <body>
                <div id="langSec">
                    <div>
                        <input name="lr" data-name="english" value="lang_en" />
                        <input name="lr" data-name="中文 (简体)" value="lang_zh-CN" />
                        <input name="lr" data-name="中文 (繁體)" value="lang_zh-TW" />
                    </div>
                </div>
            </body>
        </html>
        """
        response = mock.Mock(text=html)
        languages = google._fetch_supported_languages(response)
        self.assertEqual(type(languages), dict)
        self.assertEqual(len(languages), 3)

        self.assertIn('en', languages)
        self.assertIn('zh-CN', languages)
        self.assertIn('zh-TW', languages)

        self.assertEquals(type(languages['en']), dict)
        self.assertEquals(type(languages['zh-CN']), dict)
        self.assertEquals(type(languages['zh-TW']), dict)

        self.assertIn('name', languages['en'])
        self.assertIn('name', languages['zh-CN'])
        self.assertIn('name', languages['zh-TW'])

        self.assertEquals(languages['en']['name'], 'English')
        self.assertEquals(languages['zh-CN']['name'], u'中文 (简体)')
        self.assertEquals(languages['zh-TW']['name'], u'中文 (繁體)')
