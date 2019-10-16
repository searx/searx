from collections import defaultdict
import mock
from searx.engines import deviantart
from searx.testing import SearxTestCase


class TestDeviantartEngine(SearxTestCase):

    def test_request(self):
        dicto = defaultdict(dict)
        query = 'test_query'
        dicto['pageno'] = 0
        dicto['time_range'] = ''
        params = deviantart.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('deviantart.com' in params['url'])

    def test_no_url_in_request_year_time_range(self):
        dicto = defaultdict(dict)
        query = 'test_query'
        dicto['time_range'] = 'year'
        params = deviantart.request(query, dicto)
        self.assertEqual({}, params['url'])
