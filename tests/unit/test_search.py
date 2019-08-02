# -*- coding: utf-8 -*-

from searx.testing import SearxTestCase

import searx.preferences
import searx.search
import searx.engines


class SearchTestCase(SearxTestCase):

    @classmethod
    def setUpClass(cls):
        searx.engines.initialize_engines([{
            'name': 'general dummy',
            'engine': 'dummy',
            'categories': 'general',
            'shortcut': 'gd',
            'timeout': 3.0
        }])

    def test_timeout_simple(self):
        searx.search.max_request_timeout = None
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': 'general dummy'}],
                                               ['general'], 'en-US', 0, 1, None, None)
        search = searx.search.Search(search_query)
        search.search()
        self.assertEquals(search.actual_timeout, 3.0)

    def test_timeout_query_above_default_nomax(self):
        searx.search.max_request_timeout = None
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': 'general dummy'}],
                                               ['general'], 'en-US', 0, 1, None, 5.0)
        search = searx.search.Search(search_query)
        search.search()
        self.assertEquals(search.actual_timeout, 3.0)

    def test_timeout_query_below_default_nomax(self):
        searx.search.max_request_timeout = None
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': 'general dummy'}],
                                               ['general'], 'en-US', 0, 1, None, 1.0)
        search = searx.search.Search(search_query)
        search.search()
        self.assertEquals(search.actual_timeout, 1.0)

    def test_timeout_query_below_max(self):
        searx.search.max_request_timeout = 10.0
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': 'general dummy'}],
                                               ['general'], 'en-US', 0, 1, None, 5.0)
        search = searx.search.Search(search_query)
        search.search()
        self.assertEquals(search.actual_timeout, 5.0)

    def test_timeout_query_above_max(self):
        searx.search.max_request_timeout = 10.0
        search_query = searx.query.SearchQuery('test', [{'category': 'general', 'name': 'general dummy'}],
                                               ['general'], 'en-US', 0, 1, None, 15.0)
        search = searx.search.Search(search_query)
        search.search()
        self.assertEquals(search.actual_timeout, 10.0)
