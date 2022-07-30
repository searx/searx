from unittest.mock import patch
from requests.models import Response

from searx.testing import SearxTestCase

import searx.poolrequests
from searx.poolrequests import get_proxy_cycles, get_proxies


CONFIG = {'http': ['http://localhost:9090', 'http://localhost:9092'],
          'https': ['http://localhost:9091', 'http://localhost:9093']}


class TestProxy(SearxTestCase):

    def test_noconfig(self):
        cycles = get_proxy_cycles(None)
        self.assertIsNone(cycles)

        cycles = get_proxy_cycles(False)
        self.assertIsNone(cycles)

    def test_oldconfig(self):
        config = {
            'http': 'http://localhost:9090',
            'https': 'http://localhost:9091',
        }
        cycles = get_proxy_cycles(config)
        self.assertEqual(next(cycles['http']), 'http://localhost:9090')
        self.assertEqual(next(cycles['http']), 'http://localhost:9090')
        self.assertEqual(next(cycles['https']), 'http://localhost:9091')
        self.assertEqual(next(cycles['https']), 'http://localhost:9091')

    def test_one_proxy(self):
        config = {
            'http': ['http://localhost:9090'],
            'https': ['http://localhost:9091'],
        }
        cycles = get_proxy_cycles(config)
        self.assertEqual(next(cycles['http']), 'http://localhost:9090')
        self.assertEqual(next(cycles['http']), 'http://localhost:9090')
        self.assertEqual(next(cycles['https']), 'http://localhost:9091')
        self.assertEqual(next(cycles['https']), 'http://localhost:9091')

    def test_multiple_proxies(self):
        cycles = get_proxy_cycles(CONFIG)
        self.assertEqual(next(cycles['http']), 'http://localhost:9090')
        self.assertEqual(next(cycles['http']), 'http://localhost:9092')
        self.assertEqual(next(cycles['http']), 'http://localhost:9090')
        self.assertEqual(next(cycles['https']), 'http://localhost:9091')
        self.assertEqual(next(cycles['https']), 'http://localhost:9093')
        self.assertEqual(next(cycles['https']), 'http://localhost:9091')

    def test_getproxies_none(self):
        self.assertIsNone(get_proxies(None))

    def test_getproxies_config(self):
        cycles = get_proxy_cycles(CONFIG)
        self.assertEqual(get_proxies(cycles), {
            'http': 'http://localhost:9090',
            'https': 'http://localhost:9091'
        })
        self.assertEqual(get_proxies(cycles), {
            'http': 'http://localhost:9092',
            'https': 'http://localhost:9093'
        })

    @patch('searx.poolrequests.get_global_proxies')
    def test_request(self, mock_get_global_proxies):
        method = 'GET'
        url = 'http://localhost'
        custom_proxies = {
            'https': 'http://localhost:1080'
        }
        global_proxies = {
            'http': 'http://localhost:9092',
            'https': 'http://localhost:9093'
        }
        mock_get_global_proxies.return_value = global_proxies

        # check the global proxies usage
        with patch.object(searx.poolrequests.SessionSinglePool, 'request', return_value=Response()) as mock_method:
            searx.poolrequests.request(method, url)
        mock_method.assert_called_once_with(method=method, url=url, proxies=global_proxies)

        # check if the proxies parameter overrides the global proxies
        with patch.object(searx.poolrequests.SessionSinglePool, 'request', return_value=Response()) as mock_method:
            searx.poolrequests.request(method, url, proxies=custom_proxies)
        mock_method.assert_called_once_with(method=method, url=url, proxies=custom_proxies)
