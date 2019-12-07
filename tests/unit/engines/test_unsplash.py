from collections import defaultdict
import mock
from searx.testing import SearxTestCase
from searx.engines import unsplash


class TestUnsplashEngine(SearxTestCase):
    def test_request(self):
        query = 'penguin'
        _dict = defaultdict(dict)
        _dict['pageno'] = 1
        params = unsplash.request(query, _dict)

        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])

    def test_response(self):
        resp = mock.Mock(text='{}')
        result = unsplash.response(resp)
        self.assertEqual([], result)

        resp.text = '{"results": []}'
        result = unsplash.response(resp)
        self.assertEqual([], result)

        # Sourced from https://unsplash.com/napi/search/photos?query=penguin&xp=&per_page=20&page=2
        with open('./tests/unit/engines/unsplash_fixture.json') as fixture:
            resp.text = fixture.read()

        result = unsplash.response(resp)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'low angle photography of swimming penguin')
        self.assertEqual(result[0]['url'], 'https://unsplash.com/photos/FY8d721UO_4')
        self.assertEqual(result[0]['thumbnail_src'], 'https://images.unsplash.com/photo-1523557148507-1b77641c7e7c?ixlib=rb-0.3.5&q=80\
&fm=jpg&crop=entropy&cs=tinysrgb&w=200&fit=max')
        self.assertEqual(result[0]['img_src'], 'https://images.unsplash.com/photo-1523557148507-1b77641c7e7c\
?ixlib=rb-0.3.5')
        self.assertEqual(result[0]['content'], '')
