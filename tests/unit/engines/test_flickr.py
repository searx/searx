from collections import defaultdict
import mock
from searx.engines import flickr
from searx.testing import SearxTestCase


class TestFlickrEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = flickr.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('flickr.com' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, flickr.response, None)
        self.assertRaises(AttributeError, flickr.response, [])
        self.assertRaises(AttributeError, flickr.response, '')
        self.assertRaises(AttributeError, flickr.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(flickr.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(flickr.response(response), [])

        json = r"""
        { "photos": { "page": 1, "pages": "41001", "perpage": 100, "total": "4100032",
            "photo": [
            { "id": "15751017054", "owner": "66847915@N08",
            "secret": "69c22afc40", "server": "7285", "farm": 8,
            "title": "Photo title", "ispublic": 1,
            "isfriend": 0, "isfamily": 0,
            "description": { "_content": "Description" },
            "ownername": "Owner",
            "url_o": "https:\/\/farm8.staticflickr.com\/7285\/15751017054_9178e0f963_o.jpg",
            "height_o": "2100", "width_o": "2653",
            "url_n": "https:\/\/farm8.staticflickr.com\/7285\/15751017054_69c22afc40_n.jpg",
            "height_n": "253", "width_n": "320",
            "url_z": "https:\/\/farm8.staticflickr.com\/7285\/15751017054_69c22afc40_z.jpg",
            "height_z": "507", "width_z": "640" }
        ] }, "stat": "ok" }
        """
        response = mock.Mock(text=json)
        results = flickr.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Photo title')
        self.assertEqual(results[0]['url'], 'https://www.flickr.com/photos/66847915@N08/15751017054')
        self.assertTrue('o.jpg' in results[0]['img_src'])
        self.assertTrue('n.jpg' in results[0]['thumbnail_src'])
        self.assertTrue('Owner' in results[0]['author'])
        self.assertTrue('Description' in results[0]['content'])

        json = r"""
        { "photos": { "page": 1, "pages": "41001", "perpage": 100, "total": "4100032",
            "photo": [
            { "id": "15751017054", "owner": "66847915@N08",
            "secret": "69c22afc40", "server": "7285", "farm": 8,
            "title": "Photo title", "ispublic": 1,
            "isfriend": 0, "isfamily": 0,
            "description": { "_content": "Description" },
            "ownername": "Owner",
            "url_z": "https:\/\/farm8.staticflickr.com\/7285\/15751017054_69c22afc40_z.jpg",
            "height_z": "507", "width_z": "640" }
        ] }, "stat": "ok" }
        """
        response = mock.Mock(text=json)
        results = flickr.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Photo title')
        self.assertEqual(results[0]['url'], 'https://www.flickr.com/photos/66847915@N08/15751017054')
        self.assertTrue('z.jpg' in results[0]['img_src'])
        self.assertTrue('z.jpg' in results[0]['thumbnail_src'])
        self.assertTrue('Owner' in results[0]['author'])
        self.assertTrue('Description' in results[0]['content'])

        json = r"""
        { "photos": { "page": 1, "pages": "41001", "perpage": 100, "total": "4100032",
            "photo": [
            { "id": "15751017054", "owner": "66847915@N08",
            "secret": "69c22afc40", "server": "7285", "farm": 8,
            "title": "Photo title", "ispublic": 1,
            "isfriend": 0, "isfamily": 0,
            "description": { "_content": "Description" },
            "ownername": "Owner",
            "url_o": "https:\/\/farm8.staticflickr.com\/7285\/15751017054_9178e0f963_o.jpg",
            "height_o": "2100", "width_o": "2653" }
        ] }, "stat": "ok" }
        """
        response = mock.Mock(text=json)
        results = flickr.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Photo title')
        self.assertEqual(results[0]['url'], 'https://www.flickr.com/photos/66847915@N08/15751017054')
        self.assertTrue('o.jpg' in results[0]['img_src'])
        self.assertTrue('o.jpg' in results[0]['thumbnail_src'])
        self.assertTrue('Owner' in results[0]['author'])
        self.assertTrue('Description' in results[0]['content'])

        json = r"""
        { "photos": { "page": 1, "pages": "41001", "perpage": 100, "total": "4100032",
            "photo": [
            { "id": "15751017054", "owner": "66847915@N08",
            "secret": "69c22afc40", "server": "7285", "farm": 8,
            "title": "Photo title", "ispublic": 1,
            "isfriend": 0, "isfamily": 0,
            "description": { "_content": "Description" },
            "ownername": "Owner",
            "url_n": "https:\/\/farm8.staticflickr.com\/7285\/15751017054_69c22afc40_n.jpg",
            "height_n": "253", "width_n": "320" }
        ] }, "stat": "ok" }
        """
        response = mock.Mock(text=json)
        results = flickr.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        { "photos": { "page": 1, "pages": "41001", "perpage": 100, "total": "4100032",
            "toto": [] }, "stat": "ok" }
        """
        response = mock.Mock(text=json)
        results = flickr.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = r"""
        {"toto":[
            {"id":200,"name":"Artist Name",
            "link":"http:\/\/www.flickr.com\/artist\/1217","type":"artist"}
        ]}
        """
        response = mock.Mock(text=json)
        results = flickr.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
