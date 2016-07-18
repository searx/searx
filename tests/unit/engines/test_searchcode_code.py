from collections import defaultdict
import mock
from searx.engines import searchcode_code
from searx.testing import SearxTestCase


class TestSearchcodeCodeEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = searchcode_code.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('searchcode.com', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, searchcode_code.response, None)
        self.assertRaises(AttributeError, searchcode_code.response, [])
        self.assertRaises(AttributeError, searchcode_code.response, '')
        self.assertRaises(AttributeError, searchcode_code.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(searchcode_code.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(searchcode_code.response(response), [])

        json = """
        {
        "matchterm": "test",
        "previouspage": null,
        "searchterm": "test",
        "query": "test",
        "total": 1000,
        "page": 0,
        "nextpage": 1,
        "results": [
            {
            "repo": "https://repo",
            "linescount": 1044,
            "location": "/tests",
            "name": "Name",
            "url": "https://url",
            "md5hash": "ecac6e479edd2b9406c9e08603cec655",
            "lines": {
                "1": "// Test 011",
                "2": "// Source: "
            },
            "id": 51223527,
            "filename": "File.CPP"
            }
        ]
        }
        """
        response = mock.Mock(text=json)
        results = searchcode_code.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Name - File.CPP')
        self.assertEqual(results[0]['url'], 'https://url')
        self.assertEqual(results[0]['repository'], 'https://repo')
        self.assertEqual(results[0]['code_language'], 'cpp')

        json = r"""
        {"toto":[
            {"id":200,"name":"Artist Name",
            "link":"http:\/\/www.searchcode_code.com\/artist\/1217","type":"artist"}
        ]}
        """
        response = mock.Mock(text=json)
        results = searchcode_code.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
