from collections import defaultdict
import mock
from searx.engines import www1x
from searx.testing import SearxTestCase


class TestWww1xEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        params = www1x.request(query, defaultdict(dict))
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('1x.com' in params['url'])
