from collections import defaultdict
import mock
from searx.engines import qwant
from searx.testing import SearxTestCase


class TestQwantEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['language'] = 'fr-FR'
        qwant.categories = ['']
        params = qwant.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('web', params['url'])
        self.assertIn('qwant.com', params['url'])
        self.assertIn('fr_fr', params['url'])

        dicto['language'] = 'all'
        qwant.categories = ['news']
        params = qwant.request(query, dicto)
        self.assertFalse('fr' in params['url'])
        self.assertIn('news', params['url'])

        qwant.supported_languages = ['en', 'fr-FR', 'fr-CA']
        dicto['language'] = 'fr'
        params = qwant.request(query, dicto)
        self.assertIn('fr_fr', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, qwant.response, None)
        self.assertRaises(AttributeError, qwant.response, [])
        self.assertRaises(AttributeError, qwant.response, '')
        self.assertRaises(AttributeError, qwant.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(qwant.response(response), [])

        response = mock.Mock(text='{"data": {}}')
        self.assertEqual(qwant.response(response), [])

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
                  "date": "",
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
        qwant.categories = ['general']
        results = qwant.response(response)
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
              "items": [
                {
                  "title": "Title",
                  "score": 9999,
                  "url": "http://www.url.xyz",
                  "source": "...",
                  "media": "http://image.jpg",
                  "desc": "",
                  "thumbnail": "http://thumbnail.jpg",
                  "date": "",
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
        qwant.categories = ['images']
        results = qwant.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'http://www.url.xyz')
        self.assertEqual(results[0]['content'], '')
        self.assertEqual(results[0]['thumbnail_src'], 'http://thumbnail.jpg')
        self.assertEqual(results[0]['img_src'], 'http://image.jpg')

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
                  "date": 1433260920,
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
        qwant.categories = ['news']
        results = qwant.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'http://www.url.xyz')
        self.assertEqual(results[0]['content'], 'Description')
        self.assertIn('publishedDate', results[0])

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
                  "date": 1433260920,
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
        qwant.categories = ['social media']
        results = qwant.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'http://www.url.xyz')
        self.assertEqual(results[0]['content'], 'Description')
        self.assertIn('publishedDate', results[0])

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
                  "date": 1433260920,
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
        qwant.categories = ['']
        results = qwant.response(response)
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
        results = qwant.response(response)
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
        results = qwant.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {
          "status": "success"
        }
        """
        response = mock.Mock(text=json)
        results = qwant.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

    def test_fetch_supported_languages(self):
        page = """some code...
        config_set('project.regionalisation', {"continents":{},"languages":
        {"de":{"code":"de","name":"Deutsch","countries":["DE","CH","AT"]},
        "it":{"code":"it","name":"Italiano","countries":["IT","CH"]}}});
        some more code..."""
        response = mock.Mock(text=page)
        languages = qwant._fetch_supported_languages(response)
        self.assertEqual(type(languages), list)
        self.assertEqual(len(languages), 5)
        self.assertIn('de-DE', languages)
        self.assertIn('de-CH', languages)
        self.assertIn('de-AT', languages)
        self.assertIn('it-IT', languages)
        self.assertIn('it-CH', languages)
