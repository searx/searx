# -*- coding: utf-8 -*-

from searx.testing import SearxTestCase
from searx.preferences import Preferences
from searx.engines import engines

import searx.search


SAFESEARCH = 0
PAGENO = 1
PUBLIC_ENGINE_NAME = 'general dummy'
PRIVATE_ENGINE_NAME = 'general private offline'
TEST_ENGINES = [
    {
        'name': PUBLIC_ENGINE_NAME,
        'engine': 'dummy',
        'categories': 'general',
        'shortcut': 'gd',
        'timeout': 3.0,
        'tokens': [],
    },
    {
        'name': PRIVATE_ENGINE_NAME,
        'engine': 'dummy-offline',
        'categories': 'general',
        'shortcut': 'do',
        'timeout': 3.0,
        'offline': True,
        'tokens': ['my-token'],
    },
]


class SearchTestCase(SearxTestCase):

    @classmethod
    def setUpClass(cls):
        searx.engines.initialize_engines(TEST_ENGINES)

    def test_timeout_simple(self):
        searx.search.max_request_timeout = None
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': PUBLIC_ENGINE_NAME}],
                                               ['general'], 'en-US', SAFESEARCH, PAGENO, None, None,
                                               preferences=Preferences(['oscar'], ['general'], engines, []))
        search = searx.search.Search(search_query)
        search.search()
        self.assertEquals(search.actual_timeout, 3.0)

    def test_timeout_query_above_default_nomax(self):
        searx.search.max_request_timeout = None
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': PUBLIC_ENGINE_NAME}],
                                               ['general'], 'en-US', SAFESEARCH, PAGENO, None, 5.0,
                                               preferences=Preferences(['oscar'], ['general'], engines, []))
        search = searx.search.Search(search_query)
        search.search()
        self.assertEquals(search.actual_timeout, 3.0)

    def test_timeout_query_below_default_nomax(self):
        searx.search.max_request_timeout = None
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': PUBLIC_ENGINE_NAME}],
                                               ['general'], 'en-US', SAFESEARCH, PAGENO, None, 1.0,
                                               preferences=Preferences(['oscar'], ['general'], engines, []))
        search = searx.search.Search(search_query)
        search.search()
        self.assertEquals(search.actual_timeout, 1.0)

    def test_timeout_query_below_max(self):
        searx.search.max_request_timeout = 10.0
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': PUBLIC_ENGINE_NAME}],
                                               ['general'], 'en-US', SAFESEARCH, PAGENO, None, 5.0,
                                               preferences=Preferences(['oscar'], ['general'], engines, []))
        search = searx.search.Search(search_query)
        search.search()
        self.assertEquals(search.actual_timeout, 5.0)

    def test_timeout_query_above_max(self):
        searx.search.max_request_timeout = 10.0
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': PUBLIC_ENGINE_NAME}],
                                               ['general'], 'en-US', SAFESEARCH, PAGENO, None, 15.0,
                                               preferences=Preferences(['oscar'], ['general'], engines, []))
        search = searx.search.Search(search_query)
        search.search()
        self.assertEquals(search.actual_timeout, 10.0)

    def test_query_private_engine_without_token(self):
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': PRIVATE_ENGINE_NAME}],
                                               ['general'], 'en-US', SAFESEARCH, PAGENO, None, 2.0,
                                               preferences=Preferences(['oscar'], ['general'], engines, []))
        search = searx.search.Search(search_query)
        results = search.search()
        self.assertEquals(results.results_length(), 0)

    def test_query_private_engine_with_incorrect_token(self):
        preferences_with_tokens = Preferences(['oscar'], ['general'], engines, [])
        preferences_with_tokens.parse_dict({'tokens': 'bad-token'})
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': PRIVATE_ENGINE_NAME}],
                                               ['general'], 'en-US', SAFESEARCH, PAGENO, None, 2.0,
                                               preferences=preferences_with_tokens)
        search = searx.search.Search(search_query)
        results = search.search()
        self.assertEquals(results.results_length(), 0)

    def test_query_private_engine_with_correct_token(self):
        preferences_with_tokens = Preferences(['oscar'], ['general'], engines, [])
        preferences_with_tokens.parse_dict({'tokens': 'my-token'})
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': PRIVATE_ENGINE_NAME}],
                                               ['general'], 'en-US', SAFESEARCH, PAGENO, None, 2.0,
                                               preferences=preferences_with_tokens)
        search = searx.search.Search(search_query)
        results = search.search()
        self.assertEquals(results.results_length(), 1)
