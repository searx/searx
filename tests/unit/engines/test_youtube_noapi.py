# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import youtube_noapi
from searx.testing import SearxTestCase


class TestYoutubeNoAPIEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['time_range'] = ''
        params = youtube_noapi.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('youtube.com', params['url'])

    def test_time_range_search(self):
        dicto = defaultdict(dict)
        query = 'test_query'
        dicto['time_range'] = 'year'
        params = youtube_noapi.request(query, dicto)
        self.assertIn('&sp=EgIIBQ%253D%253D', params['url'])

        dicto['time_range'] = 'month'
        params = youtube_noapi.request(query, dicto)
        self.assertIn('&sp=EgIIBA%253D%253D', params['url'])

        dicto['time_range'] = 'week'
        params = youtube_noapi.request(query, dicto)
        self.assertIn('&sp=EgIIAw%253D%253D', params['url'])

        dicto['time_range'] = 'day'
        params = youtube_noapi.request(query, dicto)
        self.assertIn('&sp=EgIIAg%253D%253D', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, youtube_noapi.response, None)
        self.assertRaises(AttributeError, youtube_noapi.response, [])
        self.assertRaises(AttributeError, youtube_noapi.response, '')
        self.assertRaises(AttributeError, youtube_noapi.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(youtube_noapi.response(response), [])

        html = """
        <div></div>
        <script>
            window["ytInitialData"] = {
                "contents": {
                    "twoColumnSearchResultsRenderer": {
                        "primaryContents": {
                            "sectionListRenderer": {
                                "contents": [
                                    {
                                        "itemSectionRenderer": {
                                            "contents": [
                                                {
                                                    "videoRenderer": {
                                                        "videoId": "DIVZCPfAOeM",
                                                        "title": {
                                                            "simpleText": "Title"
                                                        },
                                                        "descriptionSnippet": {
                                                            "runs": [
                                                                {
                                                                    "text": "Des"
                                                                },
                                                                {
                                                                    "text": "cription"
                                                                }
                                                            ]
                                                        }
                                                    }
                                                },
                                                {
                                                    "videoRenderer": {
                                                        "videoId": "9C_HReR_McQ",
                                                        "title": {
                                                            "simpleText": "Title"
                                                        },
                                                        "descriptionSnippet": {
                                                            "simpleText": "Description"
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            };
        </script>
        """
        response = mock.Mock(text=html)
        results = youtube_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'https://www.youtube.com/watch?v=DIVZCPfAOeM')
        self.assertEqual(results[0]['content'], 'Description')
        self.assertEqual(results[0]['thumbnail'], 'https://i.ytimg.com/vi/DIVZCPfAOeM/hqdefault.jpg')
        self.assertTrue('DIVZCPfAOeM' in results[0]['embedded'])
        self.assertEqual(results[1]['title'], 'Title')
        self.assertEqual(results[1]['url'], 'https://www.youtube.com/watch?v=9C_HReR_McQ')
        self.assertEqual(results[1]['content'], 'Description')
        self.assertEqual(results[1]['thumbnail'], 'https://i.ytimg.com/vi/9C_HReR_McQ/hqdefault.jpg')
        self.assertTrue('9C_HReR_McQ' in results[1]['embedded'])

        html = """
        <ol id="item-section-063864" class="item-section">
            <li>
            </li>
        </ol>
        """
        response = mock.Mock(text=html)
        results = youtube_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
