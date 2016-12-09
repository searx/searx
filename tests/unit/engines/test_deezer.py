from collections import defaultdict
import mock
from searx.engines import deezer
from searx.testing import SearxTestCase


class TestDeezerEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = deezer.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('deezer.com' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, deezer.response, None)
        self.assertRaises(AttributeError, deezer.response, [])
        self.assertRaises(AttributeError, deezer.response, '')
        self.assertRaises(AttributeError, deezer.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(deezer.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(deezer.response(response), [])

        json = r"""
        {"data":[
            {"id":100, "title":"Title of track",
            "link":"https:\/\/www.deezer.com\/track\/1094042","duration":232,
            "artist":{"id":200,"name":"Artist Name",
                "link":"https:\/\/www.deezer.com\/artist\/1217","type":"artist"},
            "album":{"id":118106,"title":"Album Title","type":"album"},"type":"track"}
        ]}
        """
        response = mock.Mock(text=json)
        results = deezer.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title of track')
        self.assertEqual(results[0]['url'], 'https://www.deezer.com/track/1094042')
        self.assertEqual(results[0]['content'], 'Artist Name - Album Title - Title of track')
        self.assertTrue('100' in results[0]['embedded'])

        json = r"""
        {"data":[
            {"id":200,"name":"Artist Name",
            "link":"https:\/\/www.deezer.com\/artist\/1217","type":"artist"}
        ]}
        """
        response = mock.Mock(text=json)
        results = deezer.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
