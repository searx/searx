from collections import defaultdict
import mock
from searx.engines import yacy
from searx.testing import SearxTestCase


class TestYacyEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        params = yacy.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('localhost', params['url'])
        self.assertIn('fr', params['url'])

        dicto['language'] = 'all'
        params = yacy.request(query, dicto)
        self.assertIn('url', params)
        self.assertNotIn('lr=lang_', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, yacy.response, None)
        self.assertRaises(AttributeError, yacy.response, [])
        self.assertRaises(AttributeError, yacy.response, '')
        self.assertRaises(AttributeError, yacy.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(yacy.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(yacy.response(response), [])

        json = """
        {
          "channels": [
            {
              "title": "YaCy P2P-Search for test",
              "description": "Search for test",
              "link": "http://search.yacy.de:7001/yacysearch.html?query=test&amp;resource=global&amp;contentdom=0",
              "image": {
                "url": "http://search.yacy.de:7001/env/grafics/yacy.png",
                "title": "Search for test",
                "link": "http://search.yacy.de:7001/yacysearch.html?query=test&amp;resource=global&amp;contentdom=0"
              },
              "totalResults": "249",
              "startIndex": "0",
              "itemsPerPage": "5",
              "searchTerms": "test",
              "items": [
                {
                  "title": "This is the title",
                  "link": "http://this.is.the.url",
                  "code": "",
                  "description": "This should be the content",
                  "pubDate": "Sat, 08 Jun 2013 02:00:00 +0200",
                  "size": "44213",
                  "sizename": "43 kbyte",
                  "guid": "lzh_1T_5FP-A",
                  "faviconCode": "XTS4uQ_5FP-A",
                  "host": "www.gamestar.de",
                  "path": "/spiele/city-of-heroes-freedom/47019.html",
                  "file": "47019.html",
                  "urlhash": "lzh_1T_5FP-A",
                  "ranking": "0.20106804"
                },
                {
                  "title": "This is the title2",
                  "icon": "/ViewImage.png?maxwidth=96&amp;maxheight=96&amp;code=7EbAbW6BpPOA",
                  "image": "http://image.url/image.png",
                  "cache": "/ViewImage.png?quadratic=&amp;url=http://golem.ivwbox.de/cgi-bin/ivw/CP/G_INET?d=14071378",
                  "url": "http://this.is.the.url",
                  "urlhash": "7EbAbW6BpPOA",
                  "host": "www.golem.de",
                  "width": "-1",
                  "height": "-1"
                }
              ]
            }
          ]
        }
        """
        response = mock.Mock(text=json)
        results = yacy.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url')
        self.assertEqual(results[0]['content'], 'This should be the content')
        self.assertEqual(results[1]['img_src'], 'http://image.url/image.png')
        self.assertEqual(results[1]['content'], '')
        self.assertEqual(results[1]['url'], 'http://this.is.the.url')
        self.assertEqual(results[1]['title'], 'This is the title2')
