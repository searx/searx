from collections import defaultdict
import mock
from searx.engines import google_images
from searx.testing import SearxTestCase


class TestGoogleImagesEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['safesearch'] = 1
        dicto['time_range'] = ''
        params = google_images.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])

        dicto['safesearch'] = 0
        params = google_images.request(query, dicto)
        self.assertNotIn('safe', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, google_images.response, None)
        self.assertRaises(AttributeError, google_images.response, [])
        self.assertRaises(AttributeError, google_images.response, '')
        self.assertRaises(AttributeError, google_images.response, '[]')
