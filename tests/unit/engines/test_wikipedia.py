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
        params = wikipedia.request(query.encode('utf-8'), dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('test_query', params['url'])
        self.assertIn('Test_Query', params['url'])
        self.assertIn('fr.wikipedia.org', params['url'])

        query = u'Test_Query'
        params = wikipedia.request(query.encode('utf-8'), dicto)
        self.assertIn('Test_Query', params['url'])
        self.assertNotIn('test_query', params['url'])

        dicto['language'] = 'all'
        params = wikipedia.request(query, dicto)
        self.assertIn('en', params['url'])

        dicto['language'] = 'xx'
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
        response = mock.Mock(text=json, search_params=dicto)
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
        response = mock.Mock(text=json, search_params=dicto)
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
        response = mock.Mock(text=json, search_params=dicto)
        results = wikipedia.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)

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
        response = mock.Mock(text=json, search_params=dicto)
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
        response = mock.Mock(text=json, search_params=dicto)
        results = wikipedia.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[1]['infobox'], u'披頭四樂隊')
        self.assertIn(u'披头士乐队...', results[1]['content'])

    def test_fetch_supported_languages(self):
        html = u"""<html></html>"""
        response = mock.Mock(text=html)
        languages = wikipedia._fetch_supported_languages(response)
        self.assertEqual(type(languages), dict)
        self.assertEqual(len(languages), 0)

        html = u"""
        <html>
            <body>
                <div>
                    <div>
                        <h3>Table header</h3>
                        <table class="sortable jquery-tablesorter">
                            <thead>
                                <tr>
                                    <th>N</th>
                                    <th>Language</th>
                                    <th>Language (local)</th>
                                    <th>Wiki</th>
                                    <th>Articles</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>2</td>
                                    <td><a>Swedish</a></td>
                                    <td><a>Svenska</a></td>
                                    <td><a>sv</a></td>
                                    <td><a><b>3000000</b></a></td>
                                </tr>
                                <tr>
                                    <td>3</td>
                                    <td><a>Cebuano</a></td>
                                    <td><a>Sinugboanong Binisaya</a></td>
                                    <td><a>ceb</a></td>
                                    <td><a><b>3000000</b></a></td>
                                </tr>
                            </tbody>
                        </table>
                        <h3>Table header</h3>
                        <table class="sortable jquery-tablesorter">
                            <thead>
                                <tr>
                                    <th>N</th>
                                    <th>Language</th>
                                    <th>Language (local)</th>
                                    <th>Wiki</th>
                                    <th>Articles</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>2</td>
                                    <td><a>Norwegian (Bokmål)</a></td>
                                    <td><a>Norsk (Bokmål)</a></td>
                                    <td><a>no</a></td>
                                    <td><a><b>100000</b></a></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </body>
        </html>
        """
        response = mock.Mock(text=html)
        languages = wikipedia._fetch_supported_languages(response)
        self.assertEqual(type(languages), dict)
        self.assertEqual(len(languages), 3)

        self.assertIn('sv', languages)
        self.assertIn('ceb', languages)
        self.assertIn('no', languages)

        self.assertEqual(type(languages['sv']), dict)
        self.assertEqual(type(languages['ceb']), dict)
        self.assertEqual(type(languages['no']), dict)

        self.assertIn('name', languages['sv'])
        self.assertIn('english_name', languages['sv'])
        self.assertIn('articles', languages['sv'])

        self.assertEqual(languages['sv']['name'], 'Svenska')
        self.assertEqual(languages['sv']['english_name'], 'Swedish')
        self.assertEqual(languages['sv']['articles'], 3000000)
        self.assertEqual(languages['ceb']['name'], 'Sinugboanong Binisaya')
        self.assertEqual(languages['ceb']['english_name'], 'Cebuano')
        self.assertEqual(languages['ceb']['articles'], 3000000)
        self.assertEqual(languages['no']['name'], u'Norsk (Bokmål)')
        self.assertEqual(languages['no']['english_name'], u'Norwegian (Bokmål)')
        self.assertEqual(languages['no']['articles'], 100000)
