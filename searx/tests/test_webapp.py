# -*- coding: utf-8 -*-

import json
from urlparse import ParseResult
from mock import patch
from searx import webapp
from searx.testing import SearxTestCase


class ViewsTestCase(SearxTestCase):

    def setUp(self):
        webapp.app.config['TESTING'] = True  # to get better error messages
        self.app = webapp.app.test_client()

        # set some defaults
        self.test_results = [
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

        self.maxDiff = None  # to see full diffs

    def test_index_empty(self):
        result = self.app.post('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<div class="title"><h1>searx</h1></div>', result.data)

    @patch('searx.webapp.do_search')
    def test_index_html(self, search):
        search.return_value = (
            self.test_results,
            set()
        )
        result = self.app.post('/', data={'q': 'test'})
        self.assertIn(
            '<h3 class="result_title"><a href="http://first.test.xyz">First <b>Test</b></a></h3>',  # noqa
            result.data
        )
        self.assertIn(
            '<p class="content">first <b>test</b> content<br /></p>',
            result.data
        )

    @patch('searx.webapp.do_search')
    def test_index_json(self, search):
        search.return_value = (
            self.test_results,
            set()
        )
        result = self.app.post('/', data={'q': 'test', 'format': 'json'})

        result_dict = json.loads(result.data)

        self.assertEqual('test', result_dict['query'])
        self.assertEqual(
            result_dict['results'][0]['content'], 'first test content')
        self.assertEqual(
            result_dict['results'][0]['url'], 'http://first.test.xyz')

    @patch('searx.webapp.do_search')
    def test_index_csv(self, search):
        search.return_value = (
            self.test_results,
            set()
        )
        result = self.app.post('/', data={'q': 'test', 'format': 'csv'})

        self.assertEqual(
            'title,url,content,host,engine,score\r\n'
            'First Test,http://first.test.xyz,first test content,first.test.xyz,startpage,\r\n'  # noqa
            'Second Test,http://second.test.xyz,second test content,second.test.xyz,youtube,\r\n',  # noqa
            result.data
        )

    @patch('searx.webapp.do_search')
    def test_index_rss(self, search):
        search.return_value = (
            self.test_results,
            set()
        )
        result = self.app.post('/', data={'q': 'test', 'format': 'rss'})

        self.assertIn(
            '<description>Search results for "test" - searx</description>',
            result.data
        )

        self.assertIn(
            '<opensearch:totalResults>2</opensearch:totalResults>',
            result.data
        )

        self.assertIn(
            '<title>First Test</title>',
            result.data
        )

        self.assertIn(
            '<link>http://first.test.xyz</link>',
            result.data
        )

        self.assertIn(
            '<description>first test content</description>',
            result.data
        )

    def test_about(self):
        result = self.app.get('/about')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<h1>About <a href="/">searx</a></h1>', result.data)

    def test_preferences(self):
        result = self.app.get('/preferences')
        self.assertEqual(result.status_code, 200)
        self.assertIn(
            '<form method="post" action="/preferences" id="search_form">',
            result.data
        )
        self.assertIn(
            '<legend>Default categories</legend>',
            result.data
        )
        self.assertIn(
            '<legend>Interface language</legend>',
            result.data
        )

    def test_stats(self):
        result = self.app.get('/stats')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<h2>Engine stats</h2>', result.data)

    def test_robots_txt(self):
        result = self.app.get('/robots.txt')
        self.assertEqual(result.status_code, 200)
        self.assertIn('Allow: /', result.data)

    def test_opensearch_xml(self):
        result = self.app.get('/opensearch.xml')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<Description>Search searx</Description>', result.data)

    def test_favicon(self):
        result = self.app.get('/favicon.ico')
        self.assertEqual(result.status_code, 200)
