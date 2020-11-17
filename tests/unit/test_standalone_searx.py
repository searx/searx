# -*- coding: utf-8 -*-
"""Test utils/standalone_searx.py"""
import datetime
import importlib.util
import io
import sys

from mock import Mock, patch
from nose2.tools import params

from searx.search import SearchQuery
from searx.testing import SearxTestCase


def get_standalone_searx_module():
    """Get standalone_searx module."""
    module_name = 'utils.standalone_searx'
    filename = 'utils/standalone_searx.py'
    spec = importlib.util.spec_from_file_location(module_name, filename)
    sas = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sas)
    return sas


class StandaloneSearx(SearxTestCase):
    """Unit test for standalone_searx."""

    def test_parse_argument_no_args(self):
        """Test parse argument without args."""
        sas = get_standalone_searx_module()
        with patch.object(sys, 'argv', ['standalone_searx']), \
                self.assertRaises(SystemExit):
            sys.stderr = io.StringIO()
            sas.parse_argument()
            sys.stdout = sys.__stderr__

    def test_parse_argument_basic_args(self):
        """Test parse argument with basic args."""
        sas = get_standalone_searx_module()
        query = 'red box'
        exp_dict = {
            'query': query, 'category': 'general', 'lang': 'all', 'pageno': 1,
            'safesearch': '0', 'timerange': None}
        args = ['standalone_searx', query]
        with patch.object(sys, 'argv', args):
            res = sas.parse_argument()
            self.assertEqual(exp_dict, vars(res))
        res2 = sas.parse_argument(args[1:])
        self.assertEqual(exp_dict, vars(res2))

    def test_to_dict(self):
        """test to_dict."""
        sas = get_standalone_searx_module()
        self.assertEqual(
            sas.to_dict(
                sas.get_search_query(sas.parse_argument(['red box']))),
            {
                'search': {
                    'q': 'red box', 'pageno': 1, 'lang': 'all',
                    'safesearch': 0, 'timerange': None
                },
                'results': [], 'infoboxes': [], 'suggestions': [],
                'answers': [], 'paging': False, 'results_number': 0
            }
        )

    def test_to_dict_with_mock(self):
        """test to dict."""
        sas = get_standalone_searx_module()
        with patch.object(sas.searx.search, 'Search') as mock_s:
            m_search = mock_s().search()
            m_sq = Mock()
            self.assertEqual(
                sas.to_dict(m_sq),
                {
                    'answers': [],
                    'infoboxes': m_search.infoboxes,
                    'paging': m_search.paging,
                    'results': m_search.get_ordered_results(),
                    'results_number': m_search.results_number(),
                    'search': {
                        'lang': m_sq.lang,
                        'pageno': m_sq.pageno,
                        'q': m_sq.query,
                        'safesearch': m_sq.safesearch,
                        'timerange': m_sq.time_range,
                    },
                    'suggestions': []
                }
            )

    def test_get_search_query(self):
        """test get_search_query."""
        sas = get_standalone_searx_module()
        args = sas.parse_argument(['rain', ])
        search_q = sas.get_search_query(args)
        self.assertTrue(search_q)
        self.assertEqual(search_q, SearchQuery('rain', [], ['general'], 'all', 0, 1, None, None, None))

    def test_no_parsed_url(self):
        """test no_parsed_url func"""
        sas = get_standalone_searx_module()
        self.assertEqual(
            sas.no_parsed_url([{'parsed_url': 'http://example.com'}]),
            [{}]
        )

    @params(
        (datetime.datetime(2020, 1, 1), '2020-01-01T00:00:00'),
        ('a'.encode('utf8'), 'a'),
        (set([1]), [1])
    )
    def test_json_serial(self, arg, exp_res):
        """test json_serial func"""
        sas = get_standalone_searx_module()
        self.assertEqual(sas.json_serial(arg), exp_res)

    def test_json_serial_error(self):
        """test error on json_serial."""
        sas = get_standalone_searx_module()
        with self.assertRaises(TypeError):
            sas.json_serial('a')
