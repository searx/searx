from collections import defaultdict
import mock
from searx.engines import google_images
from searx.testing import SearxTestCase


class TestGoogleImagesEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = google_images.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('googleapis.com', params['url'])
        self.assertIn('safe=on', params['url'])

        dicto['safesearch'] = 0
        params = google_images.request(query, dicto)
        self.assertIn('safe=off', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, google_images.response, None)
        self.assertRaises(AttributeError, google_images.response, [])
        self.assertRaises(AttributeError, google_images.response, '')
        self.assertRaises(AttributeError, google_images.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(google_images.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(google_images.response(response), [])

        json = """
        {
        "responseData": {
            "results": [
            {
                "GsearchResultClass": "GimageSearch",
                "width": "400",
                "height": "400",
                "imageId": "ANd9GcQbYb9FJuAbG_hT4i8FeC0O0x-P--EHdzgRIF9ao97nHLl7C2mREn6qTQ",
                "tbWidth": "124",
                "tbHeight": "124",
                "unescapedUrl": "http://unescaped.url.jpg",
                "url": "http://image.url.jpg",
                "visibleUrl": "insolitebuzz.fr",
                "title": "This is the title",
                "titleNoFormatting": "Petit test sympa qui rend fou tout le monde ! A faire",
                "originalContextUrl": "http://this.is.the.url",
                "content": "<b>test</b>",
                "contentNoFormatting": "test",
                "tbUrl": "http://thumbnail.url"
            }
            ]
        },
        "responseDetails": null,
        "responseStatus": 200
        }
        """
        response = mock.Mock(text=json)
        results = google_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url')
        self.assertEqual(results[0]['thumbnail_src'], 'https://thumbnail.url')
        self.assertEqual(results[0]['img_src'], 'http://image.url.jpg')
        self.assertEqual(results[0]['content'], '<b>test</b>')

        json = """
        {
        "responseData": {
            "results": [
            {
                "GsearchResultClass": "GimageSearch",
                "width": "400",
                "height": "400",
                "imageId": "ANd9GcQbYb9FJuAbG_hT4i8FeC0O0x-P--EHdzgRIF9ao97nHLl7C2mREn6qTQ",
                "tbWidth": "124",
                "tbHeight": "124",
                "unescapedUrl": "http://unescaped.url.jpg",
                "visibleUrl": "insolitebuzz.fr",
                "title": "This is the title",
                "titleNoFormatting": "Petit test sympa qui rend fou tout le monde ! A faire",
                "originalContextUrl": "http://this.is.the.url",
                "content": "<b>test</b>",
                "contentNoFormatting": "test",
                "tbUrl": "http://thumbnail.url"
            }
            ]
        },
        "responseDetails": null,
        "responseStatus": 200
        }
        """
        response = mock.Mock(text=json)
        results = google_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {
        "responseData": {},
        "responseDetails": null,
        "responseStatus": 200
        }
        """
        response = mock.Mock(text=json)
        results = google_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
