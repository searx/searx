from collections import defaultdict
import mock
from searx.engines import mixcloud
from searx.testing import SearxTestCase


class TestMixcloudEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = mixcloud.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('mixcloud.com' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, mixcloud.response, None)
        self.assertRaises(AttributeError, mixcloud.response, [])
        self.assertRaises(AttributeError, mixcloud.response, '')
        self.assertRaises(AttributeError, mixcloud.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(mixcloud.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(mixcloud.response(response), [])

        json = """
        {"data":[
            {
            "user": {
                "url": "http://www.mixcloud.com/user/",
                "username": "user",
                "name": "User",
                "key": "/user/"
            },
            "key": "/user/this-is-the-url/",
            "created_time": "2014-11-14T13:30:02Z",
            "audio_length": 3728,
            "slug": "this-is-the-url",
            "name": "Title of track",
            "url": "http://www.mixcloud.com/user/this-is-the-url/",
            "updated_time": "2014-11-14T13:14:10Z"
        }
        ]}
        """
        response = mock.Mock(text=json)
        results = mixcloud.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title of track')
        self.assertEqual(results[0]['url'], 'http://www.mixcloud.com/user/this-is-the-url/')
        self.assertEqual(results[0]['content'], 'User')
        self.assertTrue('http://www.mixcloud.com/user/this-is-the-url/' in results[0]['embedded'])

        json = r"""
        {"toto":[
            {"id":200,"name":"Artist Name",
            "link":"http:\/\/www.mixcloud.com\/artist\/1217","type":"artist"}
        ]}
        """
        response = mock.Mock(text=json)
        results = mixcloud.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
