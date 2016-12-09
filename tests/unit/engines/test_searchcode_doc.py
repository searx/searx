from collections import defaultdict
import mock
from searx.engines import searchcode_doc
from searx.testing import SearxTestCase


class TestSearchcodeDocEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = searchcode_doc.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('searchcode.com', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, searchcode_doc.response, None)
        self.assertRaises(AttributeError, searchcode_doc.response, [])
        self.assertRaises(AttributeError, searchcode_doc.response, '')
        self.assertRaises(AttributeError, searchcode_doc.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(searchcode_doc.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(searchcode_doc.response(response), [])

        json = """
        {
        "matchterm": "test",
        "previouspage": null,
        "searchterm": "test",
        "query": "test",
        "total": 60,
        "page": 0,
        "nextpage": 1,
        "results": [
            {
            "synopsis": "Synopsis",
            "displayname": null,
            "name": "test",
            "url": "http://url",
            "type": "Type",
            "icon": null,
            "namespace": "Namespace",
            "description": "Description"
            }
        ]
        }
        """
        response = mock.Mock(text=json)
        results = searchcode_doc.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], '[Type] Namespace test')
        self.assertEqual(results[0]['url'], 'http://url')
        self.assertIn('Description', results[0]['content'])

        json = r"""
        {"toto":[
            {"id":200,"name":"Artist Name",
            "link":"http:\/\/www.searchcode_doc.com\/artist\/1217","type":"artist"}
        ]}
        """
        response = mock.Mock(text=json)
        results = searchcode_doc.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
