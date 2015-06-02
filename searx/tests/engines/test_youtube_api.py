from collections import defaultdict
import mock
from searx.engines import youtube_api
from searx.testing import SearxTestCase


class TestYoutubeAPIEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['language'] = 'fr_FR'
        params = youtube_api.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertIn('googleapis.com', params['url'])
        self.assertIn('youtube', params['url'])
        self.assertIn('fr', params['url'])

        dicto['language'] = 'all'
        params = youtube_api.request(query, dicto)
        self.assertFalse('fr' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, youtube_api.response, None)
        self.assertRaises(AttributeError, youtube_api.response, [])
        self.assertRaises(AttributeError, youtube_api.response, '')
        self.assertRaises(AttributeError, youtube_api.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(youtube_api.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(youtube_api.response(response), [])

        json = """
        {
         "kind": "youtube#searchListResponse",
         "etag": "xmg9xJZuZD438sF4hb-VcBBREXc/YJQDcTBCDcaBvl-sRZJoXdvy1ME",
         "nextPageToken": "CAUQAA",
         "pageInfo": {
          "totalResults": 1000000,
          "resultsPerPage": 20
         },
         "items": [
          {
           "kind": "youtube#searchResult",
           "etag": "xmg9xJZuZD438sF4hb-VcBBREXc/IbLO64BMhbHIgWLwLw7MDYe7Hs4",
           "id": {
            "kind": "youtube#video",
            "videoId": "DIVZCPfAOeM"
           },
           "snippet": {
            "publishedAt": "2015-05-29T22:41:04.000Z",
            "channelId": "UCNodmx1ERIjKqvcJLtdzH5Q",
            "title": "Title",
            "description": "Description",
            "thumbnails": {
             "default": {
              "url": "https://i.ytimg.com/vi/DIVZCPfAOeM/default.jpg"
             },
             "medium": {
              "url": "https://i.ytimg.com/vi/DIVZCPfAOeM/mqdefault.jpg"
             },
             "high": {
              "url": "https://i.ytimg.com/vi/DIVZCPfAOeM/hqdefault.jpg"
             }
            },
            "channelTitle": "MinecraftUniverse",
            "liveBroadcastContent": "none"
           }
          }
          ]
        }
        """
        response = mock.Mock(text=json)
        results = youtube_api.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'https://www.youtube.com/watch?v=DIVZCPfAOeM')
        self.assertEqual(results[0]['content'], 'Description')
        self.assertEqual(results[0]['thumbnail'], 'https://i.ytimg.com/vi/DIVZCPfAOeM/hqdefault.jpg')
        self.assertTrue('DIVZCPfAOeM' in results[0]['embedded'])

        json = """
        {
         "kind": "youtube#searchListResponse",
         "etag": "xmg9xJZuZD438sF4hb-VcBBREXc/YJQDcTBCDcaBvl-sRZJoXdvy1ME",
         "nextPageToken": "CAUQAA",
         "pageInfo": {
          "totalResults": 1000000,
          "resultsPerPage": 20
         }
        }
        """
        response = mock.Mock(text=json)
        results = youtube_api.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {"toto":{"entry":[]
        }
        }
        """
        response = mock.Mock(text=json)
        results = youtube_api.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
