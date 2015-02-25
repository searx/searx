from collections import defaultdict
import mock
from searx.engines import blekko_images
from searx.testing import SearxTestCase


class TestBlekkoImagesEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['safesearch'] = 1
        params = blekko_images.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('blekko.com', params['url'])
        self.assertIn('page', params['url'])

        dicto['pageno'] = 1
        params = blekko_images.request(query, dicto)
        self.assertNotIn('page', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, blekko_images.response, None)
        self.assertRaises(AttributeError, blekko_images.response, [])
        self.assertRaises(AttributeError, blekko_images.response, '')
        self.assertRaises(AttributeError, blekko_images.response, '[]')

        response = mock.Mock(text='[]')
        self.assertEqual(blekko_images.response(response), [])

        json = """
        [
            {
                "c": 1,
                "page_url": "http://result_url.html",
                "title": "Photo title",
                "tn_url": "http://ts1.mm.bing.net/th?id=HN.608050619474382748&pid=15.1",
                "url": "http://result_image.jpg"
            },
            {
                "c": 2,
                "page_url": "http://companyorange.simpsite.nl/OSM",
                "title": "OSM",
                "tn_url": "http://ts2.mm.bing.net/th?id=HN.608048068264919461&pid=15.1",
                "url": "http://simpsite.nl/userdata2/58985/Home/OSM.bmp"
            },
            {
                "c": 3,
                "page_url": "http://invincible.webklik.nl/page/osm",
                "title": "OSM",
                "tn_url": "http://ts1.mm.bing.net/th?id=HN.608024514657649476&pid=15.1",
                "url": "http://www.webklik.nl/user_files/2009_09/65324/osm.gif"
            },
            {
                "c": 4,
                "page_url": "http://www.offshorenorway.no/event/companyDetail/id/12492",
                "title": "Go to OSM Offshore AS homepage",
                "tn_url": "http://ts2.mm.bing.net/th?id=HN.608054265899847285&pid=15.1",
                "url": "http://www.offshorenorway.no/firmalogo/OSM-logo.png"
            }
        ]
        """
        response = mock.Mock(text=json)
        results = blekko_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]['title'], 'Photo title')
        self.assertEqual(results[0]['url'], 'http://result_url.html')
        self.assertEqual(results[0]['img_src'], 'http://result_image.jpg')
