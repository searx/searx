# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import wikipedia
from searx.testing import SearxTestCase


class TestWikipediaEngine(SearxTestCase):

    def test_request(self):
        wikipedia.supported_languages = ['fr', 'en']

        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['language'] = 'fr-FR'
        params = wikipedia.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('test_query', params['url'])
        self.assertIn('Test_Query', params['url'])
        self.assertIn('fr.wikipedia.org', params['url'])

        query = 'Test_Query'
        params = wikipedia.request(query, dicto)
        self.assertIn('Test_Query', params['url'])
        self.assertNotIn('test_query', params['url'])

        dicto['language'] = 'all'
        params = wikipedia.request(query, dicto)
        self.assertIn('en', params['url'])

    def test_response(self):
        dicto = defaultdict(dict)
        dicto['language'] = 'fr'

        self.assertRaises(AttributeError, wikipedia.response, None)
        self.assertRaises(AttributeError, wikipedia.response, [])
        self.assertRaises(AttributeError, wikipedia.response, '')
        self.assertRaises(AttributeError, wikipedia.response, '[]')

        # page not found
        json = """
        {
            "batchcomplete": "",
            "query": {
                "normalized": [],
                "pages": {
                    "-1": {
                        "ns": 0,
                        "title": "",
                        "missing": ""
                    }
                }
            }
        }"""
        response = mock.Mock(content=json, search_params=dicto)
        self.assertEqual(wikipedia.response(response), [])

        # normal case
        json = """
        {
            "batchcomplete": "",
            "query": {
                "normalized": [],
                "pages": {
                    "12345": {
                        "pageid": 12345,
                        "ns": 0,
                        "title": "The Title",
                        "extract": "The Title is...",
                        "thumbnail": {
                            "source": "img_src.jpg"
                        },
                        "pageimage": "img_name.jpg"
                    }
                }
            }
        }"""
        response = mock.Mock(content=json, search_params=dicto)
        results = wikipedia.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], u'The Title')
        self.assertIn('fr.wikipedia.org/wiki/The_Title', results[0]['url'])
        self.assertEqual(results[1]['infobox'], u'The Title')
        self.assertIn('fr.wikipedia.org/wiki/The_Title', results[1]['id'])
        self.assertIn('The Title is...', results[1]['content'])
        self.assertEqual(results[1]['img_src'], 'img_src.jpg')

        # disambiguation page
        json = """
        {
            "batchcomplete": "",
            "query": {
                "normalized": [],
                "pages": {
                    "12345": {
                        "pageid": 12345,
                        "ns": 0,
                        "title": "The Title",
                        "extract": "The Title can be:\\nThe Title 1\\nThe Title 2\\nThe Title 3\\nThe Title 4......................................................................................................................................." """  # noqa
        json += """
                    }
                }
            }
        }"""
        response = mock.Mock(content=json, search_params=dicto)
        results = wikipedia.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        # no image
        json = """
        {
            "batchcomplete": "",
            "query": {
                "normalized": [],
                "pages": {
                    "12345": {
                        "pageid": 12345,
                        "ns": 0,
                        "title": "The Title",
                        "extract": "The Title is......................................................................................................................................................................................." """  # noqa
        json += """
                    }
                }
            }
        }"""
        response = mock.Mock(content=json, search_params=dicto)
        results = wikipedia.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertIn('The Title is...', results[1]['content'])
        self.assertEqual(results[1]['img_src'], None)

        # title not in first paragraph
        json = u"""
        {
            "batchcomplete": "",
            "query": {
                "normalized": [],
                "pages": {
                    "12345": {
                        "pageid": 12345,
                        "ns": 0,
                        "title": "披頭四樂隊",
                        "extract": "披头士乐队....................................................................................................................................................................................................\\n披頭四樂隊...", """  # noqa
        json += """
                        "thumbnail": {
                            "source": "img_src.jpg"
                        },
                        "pageimage": "img_name.jpg"
                    }
                }
            }
        }"""
        response = mock.Mock(content=json, search_params=dicto)
        results = wikipedia.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[1]['infobox'], u'披頭四樂隊')
        self.assertIn(u'披头士乐队...', results[1]['content'])
