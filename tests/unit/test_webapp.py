# -*- coding: utf-8 -*-

import json
from urllib.parse import ParseResult
from mock import Mock
from searx import webapp
from searx.testing import SearxTestCase
from searx.search import Search


class ViewsTestCase(SearxTestCase):

    def setUp(self):
        webapp.app.config['TESTING'] = True  # to get better error messages
        self.app = webapp.app.test_client()

        # set some defaults
        test_results = [
            {
                'content': 'first test content',
                'title': 'First Test',
                'url': 'http://first.test.xyz',
                'engines': ['youtube', 'startpage'],
                'engine': 'startpage',
                'parsed_url': ParseResult(scheme='http', netloc='first.test.xyz', path='/', params='', query='', fragment=''),  # noqa
            }, {
                'content': 'second test content',
                'title': 'Second Test',
                'url': 'http://second.test.xyz',
                'engines': ['youtube', 'startpage'],
                'engine': 'youtube',
                'parsed_url': ParseResult(scheme='http', netloc='second.test.xyz', path='/', params='', query='', fragment=''),  # noqa
            },
        ]

        timings = [
            {
                'engine': 'startpage',
                'total': 0.8,
                'load': 0.7
            },
            {
                'engine': 'youtube',
                'total': 0.9,
                'load': 0.6
            }
        ]

        def search_mock(search_self, *args):
            search_self.result_container = Mock(get_ordered_results=lambda: test_results,
                                                answers=dict(),
                                                corrections=set(),
                                                suggestions=set(),
                                                infoboxes=[],
                                                unresponsive_engines=set(),
                                                results=test_results,
                                                results_number=lambda: 3,
                                                results_length=lambda: len(test_results),
                                                get_timings=lambda: timings,
                                                redirect_url=None)

        self.setattr4test(Search, 'search', search_mock)

        def get_current_theme_name_mock(override=None):
            if override:
                return override
            return 'legacy'

        self.setattr4test(webapp, 'get_current_theme_name', get_current_theme_name_mock)

        self.maxDiff = None  # to see full diffs

    def test_index_empty(self):
        result = self.app.post('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'<div class="title"><h1>searx</h1></div>', result.data)

    def test_index_html_post(self):
        result = self.app.post('/', data={'q': 'test'})
        self.assertEqual(result.status_code, 308)
        self.assertEqual(result.location, 'http://localhost/search')

    def test_index_html_get(self):
        result = self.app.post('/?q=test')
        self.assertEqual(result.status_code, 308)
        self.assertEqual(result.location, 'http://localhost/search?q=test')

    def test_search_empty_html(self):
        result = self.app.post('/search', data={'q': ''})
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'<div class="title"><h1>searx</h1></div>', result.data)

    def test_search_empty_json(self):
        result = self.app.post('/search', data={'q': '', 'format': 'json'})
        self.assertEqual(result.status_code, 400)

    def test_search_empty_csv(self):
        result = self.app.post('/search', data={'q': '', 'format': 'csv'})
        self.assertEqual(result.status_code, 400)

    def test_search_empty_rss(self):
        result = self.app.post('/search', data={'q': '', 'format': 'rss'})
        self.assertEqual(result.status_code, 400)

    def test_search_html(self):
        result = self.app.post('/search', data={'q': 'test'})

        self.assertIn(
            b'<h3 class="result_title"><img width="14" height="14" class="favicon" src="/static/themes/legacy/img/icons/icon_youtube.ico" alt="youtube" /><a href="http://second.test.xyz" rel="noreferrer">Second <span class="highlight">Test</span></a></h3>',  # noqa
            result.data
        )
        self.assertIn(
            b'<p class="content">first <span class="highlight">test</span> content<br class="last"/></p>',  # noqa
            result.data
        )

    def test_index_json(self):
        result = self.app.post('/', data={'q': 'test', 'format': 'json'})
        self.assertEqual(result.status_code, 308)

    def test_search_json(self):
        result = self.app.post('/search', data={'q': 'test', 'format': 'json'})
        result_dict = json.loads(result.data.decode())

        self.assertEqual('test', result_dict['query'])
        self.assertEqual(len(result_dict['results']), 2)
        self.assertEqual(result_dict['results'][0]['content'], 'first test content')
        self.assertEqual(result_dict['results'][0]['url'], 'http://first.test.xyz')

    def test_index_csv(self):
        result = self.app.post('/', data={'q': 'test', 'format': 'csv'})
        self.assertEqual(result.status_code, 308)

    def test_search_csv(self):
        result = self.app.post('/search', data={'q': 'test', 'format': 'csv'})

        self.assertEqual(
            b'title,url,content,host,engine,score,type\r\n'
            b'First Test,http://first.test.xyz,first test content,first.test.xyz,startpage,,result\r\n'  # noqa
            b'Second Test,http://second.test.xyz,second test content,second.test.xyz,youtube,,result\r\n',  # noqa
            result.data
        )

    def test_index_rss(self):
        result = self.app.post('/', data={'q': 'test', 'format': 'rss'})
        self.assertEqual(result.status_code, 308)

    def test_index_rss(self):
        result = self.app.post('/search', data={'q': 'test', 'format': 'rss'})

        self.assertIn(
            b'<description>Search results for "test" - searx</description>',
            result.data
        )

        self.assertIn(
            b'<opensearch:totalResults>3</opensearch:totalResults>',
            result.data
        )

        self.assertIn(
            b'<title>First Test</title>',
            result.data
        )

        self.assertIn(
            b'<link>http://first.test.xyz</link>',
            result.data
        )

        self.assertIn(
            b'<description>first test content</description>',
            result.data
        )

    def test_about(self):
        result = self.app.get('/about')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'<h1>About <a href="/">searx</a></h1>', result.data)

    def test_preferences(self):
        result = self.app.get('/preferences')
        self.assertEqual(result.status_code, 200)
        self.assertIn(
            b'<form method="post" action="/preferences" id="search_form">',
            result.data
        )
        self.assertIn(
            b'<legend>Default categories</legend>',
            result.data
        )
        self.assertIn(
            b'<legend>Interface language</legend>',
            result.data
        )

    def test_stats(self):
        result = self.app.get('/stats')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'<h2>Engine stats</h2>', result.data)

    def test_robots_txt(self):
        result = self.app.get('/robots.txt')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Allow: /', result.data)

    def test_opensearch_xml(self):
        result = self.app.get('/opensearch.xml')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'<Description>a privacy-respecting, hackable metasearch engine</Description>', result.data)

    def test_favicon(self):
        result = self.app.get('/favicon.ico')
        self.assertEqual(result.status_code, 200)

    def test_config(self):
        result = self.app.get('/config')
        self.assertEqual(result.status_code, 200)
        json_result = result.get_json()
        self.assertTrue(json_result)
