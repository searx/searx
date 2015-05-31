from collections import defaultdict
import mock
from searx.engines import qwant_images
from searx.testing import SearxTestCase


class TestQwantImagesEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['language'] = 'fr_FR'
        params = qwant_images.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('qwant.com', params['url'])
        self.assertIn('fr_fr', params['url'])

        dicto['language'] = 'all'
        params = qwant_images.request(query, dicto)
        self.assertFalse('fr' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, qwant_images.response, None)
        self.assertRaises(AttributeError, qwant_images.response, [])
        self.assertRaises(AttributeError, qwant_images.response, '')
        self.assertRaises(AttributeError, qwant_images.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(qwant_images.response(response), [])

        response = mock.Mock(text='{"data": {}}')
        self.assertEqual(qwant_images.response(response), [])

        json = """
        {
          "status": "success",
          "data": {
            "query": {
              "locale": "en_us",
              "query": "Test",
              "offset": 10
            },
            "result": {
              "items": [
                {
                  "title": "Title",
                  "type": "image",
                  "media": "http://www.url.xyz/fullimage.jpg",
                  "desc": "",
                  "thumbnail": "http://www.url.xyz/thumbnail.jpg",
                  "thumb_width": 365,
                  "thumb_height": 230,
                  "width": "365",
                  "height": "230",
                  "size": "187.7KB",
                  "url": "http://www.url.xyz",
                  "_id": "0ffd93fb26f3e192a6020af8fc16fbb1",
                  "media_fullsize": "http://www.proxy/fullimage.jpg",
                  "count": 0
                }
              ],
              "filters": []
            },
            "cache": {
              "key": "e66aa864c00147a0e3a16ff7a5efafde",
              "created": 1433092754,
              "expiration": 259200,
              "status": "miss",
              "age": 0
            }
          }
        }
        """
        response = mock.Mock(text=json)
        results = qwant_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'http://www.url.xyz')
        self.assertEqual(results[0]['content'], '')
        self.assertEqual(results[0]['thumbnail_src'], 'http://www.url.xyz/thumbnail.jpg')
        self.assertEqual(results[0]['img_src'], 'http://www.url.xyz/fullimage.jpg')

        json = """
        {
          "status": "success",
          "data": {
            "query": {
              "locale": "en_us",
              "query": "Test",
              "offset": 10
            },
            "result": {
              "filters": []
            },
            "cache": {
              "key": "e66aa864c00147a0e3a16ff7a5efafde",
              "created": 1433092754,
              "expiration": 259200,
              "status": "miss",
              "age": 0
            }
          }
        }
        """
        response = mock.Mock(text=json)
        results = qwant_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {
          "status": "success",
          "data": {
            "query": {
              "locale": "en_us",
              "query": "Test",
              "offset": 10
            },
            "cache": {
              "key": "e66aa864c00147a0e3a16ff7a5efafde",
              "created": 1433092754,
              "expiration": 259200,
              "status": "miss",
              "age": 0
            }
          }
        }
        """
        response = mock.Mock(text=json)
        results = qwant_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {
          "status": "success"
        }
        """
        response = mock.Mock(text=json)
        results = qwant_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
