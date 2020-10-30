# -*- coding: utf-8 -*-
"""Test utils/standalone_searx.py"""
import importlib.util
import sys

from mock import patch

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
            sas.parse_argument()

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

    def test_main_basic_args(self):
        """test basic args for main func."""
        sas = get_standalone_searx_module()
        res = sas.main(sas.parse_argument(['red box']))
        self.assertTrue(res)
