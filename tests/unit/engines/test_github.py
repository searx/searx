from collections import defaultdict
import mock
from searx.engines import github
from searx.testing import SearxTestCase


class TestGitHubEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        params = github.request(query, defaultdict(dict))
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('github.com' in params['url'])
        self.assertEqual(params['headers']['Accept'], github.accept_header)

    def test_response(self):
        self.assertRaises(AttributeError, github.response, None)
        self.assertRaises(AttributeError, github.response, [])
        self.assertRaises(AttributeError, github.response, '')
        self.assertRaises(AttributeError, github.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(github.response(response), [])

        response = mock.Mock(text='{"items": []}')
        self.assertEqual(github.response(response), [])

        json = """
        {
            "items": [
                {
                    "name": "title",
                    "html_url": "url",
                    "description": ""
                }
            ]
        }
        """
        response = mock.Mock(text=json)
        results = github.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'title')
        self.assertEqual(results[0]['url'], 'url')
        self.assertEqual(results[0]['content'], '')

        json = """
        {
            "items": [
                {
                    "name": "title",
                    "html_url": "url",
                    "description": "desc"
                }
            ]
        }
        """
        response = mock.Mock(text=json)
        results = github.response(response)
        self.assertEqual(results[0]['content'], "desc")
