from collections import defaultdict
import mock
from searx.engines import flickr_noapi
from searx.testing import SearxTestCase


class TestFlickrNoapiEngine(SearxTestCase):

    def test_build_flickr_url(self):
        url = flickr_noapi.build_flickr_url("uid", "pid")
        self.assertIn("uid", url)
        self.assertIn("pid", url)

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = flickr_noapi.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('flickr.com', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, flickr_noapi.response, None)
        self.assertRaises(AttributeError, flickr_noapi.response, [])
        self.assertRaises(AttributeError, flickr_noapi.response, '')
        self.assertRaises(AttributeError, flickr_noapi.response, '[]')

        response = mock.Mock(text='"search-photos-models","photos":{},"totalItems":')
        self.assertEqual(flickr_noapi.response(response), [])

        response = mock.Mock(text='search-photos-models","photos":{"data": []},"totalItems":')
        self.assertEqual(flickr_noapi.response(response), [])

        json = """
        "search-photos-models","photos":
        {
          "_data": [
            {
              "_flickrModelRegistry": "photo-models",
              "title": "This is the title",
              "sizes": {
                "c": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_c.jpg",
                  "width": 541,
                  "height": 800,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_c.jpg",
                  "key": "c"
                },
                "h": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_761d32237a_h.jpg",
                  "width": 1081,
                  "height": 1600,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_761d32237a_h.jpg",
                  "key": "h"
                },
                "k": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_f145a2c11a_k.jpg",
                  "width": 1383,
                  "height": 2048,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_f145a2c11a_k.jpg",
                  "key": "k"
                },
                "l": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_b.jpg",
                  "width": 692,
                  "height": 1024,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_b.jpg",
                  "key": "l"
                },
                "m": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777.jpg",
                  "width": 338,
                  "height": 500,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777.jpg",
                  "key": "m"
                },
                "n": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_n.jpg",
                  "width": 216,
                  "height": 320,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_n.jpg",
                  "key": "n"
                },
                "q": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_q.jpg",
                  "width": 150,
                  "height": 150,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_q.jpg",
                  "key": "q"
                },
                "s": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_m.jpg",
                  "width": 162,
                  "height": 240,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_m.jpg",
                  "key": "s"
                },
                "sq": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_s.jpg",
                  "width": 75,
                  "height": 75,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_s.jpg",
                  "key": "sq"
                },
                "t": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_t.jpg",
                  "width": 68,
                  "height": 100,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_t.jpg",
                  "key": "t"
                },
                "z": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_z.jpg",
                  "width": 433,
                  "height": 640,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_z.jpg",
                  "key": "z"
                }
              },
              "canComment": false,
              "rotation": 0,
              "owner": {
                "_flickrModelRegistry": "person-models",
                "pathAlias": "klink692",
                "username": "Owner",
                "buddyicon": {
                  "retina": null,
                  "large": null,
                  "medium": null,
                  "small": null,
                  "default": "//c1.staticflickr.com/9/8108/buddyicons/59729010@N00.jpg?1361642376#59729010@N00"
                },
                "isPro": true,
                "id": "59729010@N00"
              },
              "engagement": {
                "_flickrModelRegistry": "photo-engagement-models",
                "ownerNsid": "59729010@N00",
                "faveCount": 21,
                "commentCount": 14,
                "viewCount": 10160,
                "id": "14001294434"
              },
              "description": "Description",
              "isHD": false,
              "secret": "410f653777",
              "canAddMeta": false,
              "license": 0,
              "oWidth": 1803,
              "oHeight": 2669,
              "safetyLevel": 0,
              "id": "14001294434"
            }
          ],
          "fetchedStart": true,
          "fetchedEnd": false,
          "totalItems": "4386039"
        },"totalItems":
        """
        json = json.replace('\r\n', '').replace('\n', '').replace('\r', '')
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://www.flickr.com/photos/59729010@N00/14001294434')
        self.assertIn('k.jpg', results[0]['img_src'])
        self.assertIn('n.jpg', results[0]['thumbnail_src'])
        self.assertIn('Owner', results[0]['content'])
        self.assertIn('Description', results[0]['content'])

        json = """
        "search-photos-models","photos":
        {
          "_data": [
            {
              "_flickrModelRegistry": "photo-models",
              "title": "This is the title",
              "sizes": {
                "z": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_z.jpg",
                  "width": 433,
                  "height": 640,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_z.jpg",
                  "key": "z"
                }
              },
              "canComment": false,
              "rotation": 0,
              "owner": {
                "_flickrModelRegistry": "person-models",
                "pathAlias": "klink692",
                "username": "Owner",
                "buddyicon": {
                  "retina": null,
                  "large": null,
                  "medium": null,
                  "small": null,
                  "default": "//c1.staticflickr.com/9/8108/buddyicons/59729010@N00.jpg?1361642376#59729010@N00"
                },
                "isPro": true,
                "id": "59729010@N00"
              },
              "engagement": {
                "_flickrModelRegistry": "photo-engagement-models",
                "ownerNsid": "59729010@N00",
                "faveCount": 21,
                "commentCount": 14,
                "viewCount": 10160,
                "id": "14001294434"
              },
              "description": "Description",
              "isHD": false,
              "secret": "410f653777",
              "canAddMeta": false,
              "license": 0,
              "oWidth": 1803,
              "oHeight": 2669,
              "safetyLevel": 0,
              "id": "14001294434"
            }
          ],
          "fetchedStart": true,
          "fetchedEnd": false,
          "totalItems": "4386039"
        },"totalItems":
        """
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://www.flickr.com/photos/59729010@N00/14001294434')
        self.assertIn('z.jpg', results[0]['img_src'])
        self.assertIn('z.jpg', results[0]['thumbnail_src'])
        self.assertIn('Owner', results[0]['content'])
        self.assertIn('Description', results[0]['content'])

        json = """
        "search-photos-models","photos":
        {
          "_data": [
            {
              "_flickrModelRegistry": "photo-models",
              "title": "This is the title",
              "sizes": {
                "o": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_o.jpg",
                  "width": 433,
                  "height": 640,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_o.jpg",
                  "key": "o"
                }
              },
              "canComment": false,
              "rotation": 0,
              "owner": {
                "_flickrModelRegistry": "person-models",
                "pathAlias": "klink692",
                "username": "Owner",
                "buddyicon": {
                  "retina": null,
                  "large": null,
                  "medium": null,
                  "small": null,
                  "default": "//c1.staticflickr.com/9/8108/buddyicons/59729010@N00.jpg?1361642376#59729010@N00"
                },
                "isPro": true,
                "id": "59729010@N00"
              },
              "engagement": {
                "_flickrModelRegistry": "photo-engagement-models",
                "ownerNsid": "59729010@N00",
                "faveCount": 21,
                "commentCount": 14,
                "viewCount": 10160,
                "id": "14001294434"
              },
              "isHD": false,
              "secret": "410f653777",
              "canAddMeta": false,
              "license": 0,
              "oWidth": 1803,
              "oHeight": 2669,
              "safetyLevel": 0,
              "id": "14001294434"
            }
          ],
          "fetchedStart": true,
          "fetchedEnd": false,
          "totalItems": "4386039"
        },"totalItems":
        """
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://www.flickr.com/photos/59729010@N00/14001294434')
        self.assertIn('o.jpg', results[0]['img_src'])
        self.assertIn('o.jpg', results[0]['thumbnail_src'])
        self.assertIn('Owner', results[0]['content'])

        json = """
        "search-photos-models","photos":
        {
          "_data": [
            {
              "_flickrModelRegistry": "photo-models",
              "title": "This is the title",
              "sizes": {
              },
              "canComment": false,
              "rotation": 0,
              "owner": {
                "_flickrModelRegistry": "person-models",
                "pathAlias": "klink692",
                "username": "Owner",
                "buddyicon": {
                  "retina": null,
                  "large": null,
                  "medium": null,
                  "small": null,
                  "default": "//c1.staticflickr.com/9/8108/buddyicons/59729010@N00.jpg?1361642376#59729010@N00"
                },
                "isPro": true,
                "id": "59729010@N00"
              },
              "engagement": {
                "_flickrModelRegistry": "photo-engagement-models",
                "ownerNsid": "59729010@N00",
                "faveCount": 21,
                "commentCount": 14,
                "viewCount": 10160,
                "id": "14001294434"
              },
              "description": "Description",
              "isHD": false,
              "secret": "410f653777",
              "canAddMeta": false,
              "license": 0,
              "oWidth": 1803,
              "oHeight": 2669,
              "safetyLevel": 0,
              "id": "14001294434"
            }
          ],
          "fetchedStart": true,
          "fetchedEnd": false,
          "totalItems": "4386039"
        },"totalItems":
        """
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        "search-photos-models","photos":
        {
          "_data": [null],
          "fetchedStart": true,
          "fetchedEnd": false,
          "totalItems": "4386039"
        },"totalItems":
        """
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        "search-photos-models","photos":
        {
          "_data": [
            {
              "_flickrModelRegistry": "photo-models",
              "title": "This is the title",
              "sizes": {
                "o": {
                  "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_o.jpg",
                  "width": 433,
                  "height": 640,
                  "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_o.jpg",
                  "key": "o"
                }
              },
              "canComment": false,
              "rotation": 0,
              "owner": {
                "_flickrModelRegistry": "person-models",
                "pathAlias": "klink692",
                "username": "Owner",
                "buddyicon": {
                  "retina": null,
                  "large": null,
                  "medium": null,
                  "small": null,
                  "default": "//c1.staticflickr.com/9/8108/buddyicons/59729010@N00.jpg?1361642376#59729010@N00"
                },
                "isPro": true
              },
              "engagement": {
                "_flickrModelRegistry": "photo-engagement-models",
                "ownerNsid": "59729010@N00",
                "faveCount": 21,
                "commentCount": 14,
                "viewCount": 10160,
                "id": "14001294434"
              },
              "description": "Description",
              "isHD": false,
              "secret": "410f653777",
              "canAddMeta": false,
              "license": 0,
              "oWidth": 1803,
              "oHeight": 2669,
              "safetyLevel": 0,
              "id": "14001294434"
            }
          ],
          "fetchedStart": true,
          "fetchedEnd": false,
          "totalItems": "4386039"
        },"totalItems":
        """
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {"toto":[
            {"id":200,"name":"Artist Name",
            "link":"http:\/\/www.flickr.com\/artist\/1217","type":"artist"}
        ]}
        """
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
