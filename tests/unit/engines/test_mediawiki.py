# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import mediawiki
from searx.testing import SearxTestCase


class TestMediawikiEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        params = mediawiki.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('wikipedia.org', params['url'])
        self.assertIn('fr', params['url'])

        dicto['language'] = 'all'
        params = mediawiki.request(query, dicto)
        self.assertIn('en', params['url'])

        mediawiki.base_url = "http://test.url/"
        mediawiki.search_url = mediawiki.base_url +\
                                 'w/api.php?action=query'\
                                 '&list=search'\
                                 '&{query}'\
                                 '&srprop=timestamp'\
                                 '&format=json'\
                                 '&sroffset={offset}'\
                                 '&srlimit={limit}'     # noqa
        params = mediawiki.request(query, dicto)
        self.assertIn('test.url', params['url'])

    def test_response(self):
        dicto = defaultdict(dict)
        dicto['language'] = 'fr'
        mediawiki.base_url = "https://{language}.wikipedia.org/"

        self.assertRaises(AttributeError, mediawiki.response, None)
        self.assertRaises(AttributeError, mediawiki.response, [])
        self.assertRaises(AttributeError, mediawiki.response, '')
        self.assertRaises(AttributeError, mediawiki.response, '[]')

        response = mock.Mock(text='{}', search_params=dicto)
        self.assertEqual(mediawiki.response(response), [])

        response = mock.Mock(text='{"data": []}', search_params=dicto)
        self.assertEqual(mediawiki.response(response), [])

        json = """
        {
            "query-continue": {
                "search": {
                    "sroffset": 1
                }
            },
            "query": {
                "searchinfo": {
                    "totalhits": 29721
                },
                "search": [
                    {
                        "ns": 0,
                        "title": "This is the title étude",
                        "timestamp": "2014-12-19T17:42:52Z"
                    }
                ]
            }
        }
        """
        response = mock.Mock(text=json, search_params=dicto)
        results = mediawiki.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], u'This is the title étude')
        self.assertIn('fr.wikipedia.org', results[0]['url'])
        self.assertIn('This_is_the_title', results[0]['url'])
        self.assertIn('%C3%A9tude', results[0]['url'])
        self.assertEqual(results[0]['content'], '')

        json = """
        {
            "query-continue": {
                "search": {
                    "sroffset": 1
                }
            },
            "query": {
                "searchinfo": {
                    "totalhits": 29721
                },
                "search": [
                ]
            }
        }
        """
        response = mock.Mock(text=json, search_params=dicto)
        results = mediawiki.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {
            "query-continue": {
                "search": {
                    "sroffset": 1
                }
            },
            "query": {
            }
        }
        """
        response = mock.Mock(text=json, search_params=dicto)
        results = mediawiki.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = r"""
        {"toto":[
            {"id":200,"name":"Artist Name",
            "link":"http:\/\/www.mediawiki.com\/artist\/1217","type":"artist"}
        ]}
        """
        response = mock.Mock(text=json, search_params=dicto)
        results = mediawiki.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
