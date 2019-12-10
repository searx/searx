from collections import defaultdict
import mock
from searx.engines import digg
from searx.testing import SearxTestCase


class TestDiggEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = digg.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('digg.com', params['url'])
