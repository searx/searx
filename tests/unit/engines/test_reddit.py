from collections import defaultdict
import mock
from searx.engines import reddit
from searx.testing import SearxTestCase
from datetime import datetime


class TestRedditEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dic = defaultdict(dict)
        params = reddit.request(query, dic)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('reddit.com' in params['url'])

    def test_response(self):
        resp = mock.Mock(text='{}')
        self.assertEqual(reddit.response(resp), [])

        json = """
        {
            "kind": "Listing",
            "data": {
                "children": [{
                    "data": {
                        "url": "http://google2.com/",
                        "permalink": "http://google.com/",
                        "title": "Title number one",
                        "selftext": "Sample",
                        "created_utc": 1401219957.0,
                        "thumbnail": "http://image.com/picture.jpg"
                    }
                }, {
                    "data": {
                        "url": "https://reddit2.com/",
                        "permalink": "https://reddit.com/",
                        "title": "Title number two",
                        "selftext": "Dominus vobiscum",
                        "created_utc": 1438792533.0,
                        "thumbnail": "self"
                    }
                }]
            }
        }
        """

        resp = mock.Mock(text=json)
        results = reddit.response(resp)

        self.assertEqual(len(results), 2)
        self.assertEqual(type(results), list)

        # testing first result (picture)
        r = results[0]
        self.assertEqual(r['url'], 'http://google.com/')
        self.assertEqual(r['title'], 'Title number one')
        self.assertEqual(r['template'], 'images.html')
        self.assertEqual(r['img_src'], 'http://google2.com/')
        self.assertEqual(r['thumbnail_src'], 'http://image.com/picture.jpg')

        # testing second result (self-post)
        r = results[1]
        self.assertEqual(r['url'], 'https://reddit.com/')
        self.assertEqual(r['title'], 'Title number two')
        self.assertEqual(r['content'], 'Dominus vobiscum')
        created = datetime.fromtimestamp(1438792533.0)
        self.assertEqual(r['publishedDate'], created)
        self.assertTrue('thumbnail_src' not in r)
        self.assertTrue('img_src' not in r)
