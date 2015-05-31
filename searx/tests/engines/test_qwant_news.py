from collections import defaultdict
import mock
from searx.engines import qwant_news
from searx.testing import SearxTestCase


class TestQwantNewsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['language'] = 'fr_FR'
        params = qwant_news.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('qwant.com', params['url'])
        self.assertIn('fr_fr', params['url'])

        dicto['language'] = 'all'
        params = qwant_news.request(query, dicto)
        self.assertFalse('fr' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, qwant_news.response, None)
        self.assertRaises(AttributeError, qwant_news.response, [])
        self.assertRaises(AttributeError, qwant_news.response, '')
        self.assertRaises(AttributeError, qwant_news.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(qwant_news.response(response), [])

        response = mock.Mock(text='{"data": {}}')
        self.assertEqual(qwant_news.response(response), [])

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
                  "score": 9999,
                  "url": "http://www.url.xyz",
                  "source": "...",
                  "desc": "Description",
                  "date": 1433065411,
                  "_id": "db0aadd62c2a8565567ffc382f5c61fa",
                  "favicon": "https://s.qwant.com/fav.ico"
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
        results = qwant_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'http://www.url.xyz')
        self.assertEqual(results[0]['content'], 'Description')

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
        results = qwant_news.response(response)
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
        results = qwant_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {
          "status": "success"
        }
        """
        response = mock.Mock(text=json)
        results = qwant_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
