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
        dicto['time_range'] = ''
        params = flickr_noapi.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('flickr.com', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, flickr_noapi.response, None)
        self.assertRaises(AttributeError, flickr_noapi.response, [])
        self.assertRaises(AttributeError, flickr_noapi.response, '')
        self.assertRaises(AttributeError, flickr_noapi.response, '[]')

        response = mock.Mock(text='"modelExport:{"legend":[],"main":{"search-photos-lite-models":[{"photos":{}}]}}')
        self.assertEqual(flickr_noapi.response(response), [])

        response = \
            mock.Mock(text='"modelExport:{"legend":[],"main":{"search-photos-lite-models":[{"photos":{"_data":[]}}]}}')
        self.assertEqual(flickr_noapi.response(response), [])

        # everthing is ok test
        json = """
        modelExport: {
          "legend": [
            [
              "search-photos-lite-models",
              "0",
              "photos",
              "_data",
              "0"
            ]
          ],
          "main": {
            "search-photos-lite-models": [
              {
                "photos": {
                  "_data": [
                    {
                      "_flickrModelRegistry": "photo-lite-models",
                      "title": "This%20is%20the%20title",
                      "username": "Owner",
                      "pathAlias": "klink692",
                      "realname": "Owner",
                      "license": 0,
                      "ownerNsid": "59729010@N00",
                      "canComment": false,
                      "commentCount": 14,
                      "faveCount": 21,
                      "id": "14001294434",
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
                      }
                    }
                  ]
                }
              }
            ]
          }
        }
        """
        # Flickr serves search results in a json block named 'modelExport' buried inside a script tag,
        # this json is served as a single line terminating with a comma.
        json = ''.join(json.split()) + ',\n'
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://www.flickr.com/photos/59729010@N00/14001294434')
        self.assertIn('k.jpg', results[0]['img_src'])
        self.assertIn('n.jpg', results[0]['thumbnail_src'])
        self.assertIn('Owner', results[0]['author'])

        # no n size, only the z size
        json = """
        modelExport: {
          "legend": [
            [
              "search-photos-lite-models",
              "0",
              "photos",
              "_data",
              "0"
            ]
          ],
          "main": {
            "search-photos-lite-models": [
              {
                "photos": {
                  "_data": [
                    {
                      "_flickrModelRegistry": "photo-lite-models",
                      "title": "This%20is%20the%20title",
                      "username": "Owner",
                      "pathAlias": "klink692",
                      "realname": "Owner",
                      "license": 0,
                      "ownerNsid": "59729010@N00",
                      "canComment": false,
                      "commentCount": 14,
                      "faveCount": 21,
                      "id": "14001294434",
                      "sizes": {
                        "z": {
                          "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_z.jpg",
                          "width": 433,
                          "height": 640,
                          "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_z.jpg",
                          "key": "z"
                        }
                      }
                    }
                  ]
                }
              }
            ]
          }
        }
        """
        json = ''.join(json.split()) + ',\n'
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://www.flickr.com/photos/59729010@N00/14001294434')
        self.assertIn('z.jpg', results[0]['img_src'])
        self.assertIn('z.jpg', results[0]['thumbnail_src'])
        self.assertIn('Owner', results[0]['author'])

        # no z or n size
        json = """
        modelExport: {
          "legend": [
            [
              "search-photos-lite-models",
              "0",
              "photos",
              "_data",
              "0"
            ]
          ],
          "main": {
            "search-photos-lite-models": [
              {
                "photos": {
                  "_data": [
                    {
                      "_flickrModelRegistry": "photo-lite-models",
                      "title": "This%20is%20the%20title",
                      "username": "Owner",
                      "pathAlias": "klink692",
                      "realname": "Owner",
                      "license": 0,
                      "ownerNsid": "59729010@N00",
                      "canComment": false,
                      "commentCount": 14,
                      "faveCount": 21,
                      "id": "14001294434",
                      "sizes": {
                        "o": {
                          "displayUrl": "//farm8.staticflickr.com/7246/14001294434_410f653777_o.jpg",
                          "width": 433,
                          "height": 640,
                          "url": "//c4.staticflickr.com/8/7246/14001294434_410f653777_o.jpg",
                          "key": "o"
                        }
                      }
                    }
                  ]
                }
              }
            ]
          }
        }
        """
        json = ''.join(json.split()) + ',\n'
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://www.flickr.com/photos/59729010@N00/14001294434')
        self.assertIn('o.jpg', results[0]['img_src'])
        self.assertIn('o.jpg', results[0]['thumbnail_src'])
        self.assertIn('Owner', results[0]['author'])

        # no image test
        json = """
        modelExport: {
          "legend": [
            [
              "search-photos-lite-models",
              "0",
              "photos",
              "_data",
              "0"
            ]
          ],
          "main": {
            "search-photos-lite-models": [
              {
                "photos": {
                  "_data": [
                    {
                      "_flickrModelRegistry": "photo-lite-models",
                      "title": "This is the title",
                      "username": "Owner",
                      "pathAlias": "klink692",
                      "realname": "Owner",
                      "license": 0,
                      "ownerNsid": "59729010@N00",
                      "canComment": false,
                      "commentCount": 14,
                      "faveCount": 21,
                      "id": "14001294434",
                      "sizes": {
                      }
                    }
                  ]
                }
              }
            ]
          }
        }
        """
        json = ''.join(json.split()) + ',\n'
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        # null test
        json = """
        modelExport: {
          "legend": [null],
          "main": {
            "search-photos-lite-models": [
              {
                "photos": {
                  "_data": [null]
                }
              }
            ]
          }
        }
        """
        json = ''.join(json.split()) + ',\n'
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        # garbage test
        json = r"""
        {"toto":[
            {"id":200,"name":"Artist Name",
            "link":"http:\/\/www.flickr.com\/artist\/1217","type":"artist"}
        ]}
        """
        json = ''.join(json.split()) + ',\n'
        response = mock.Mock(text=json)
        results = flickr_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
