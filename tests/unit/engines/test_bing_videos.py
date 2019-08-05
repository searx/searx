# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import bing_videos
from searx.testing import SearxTestCase


class TestBingVideosEngine(SearxTestCase):

    def test_request(self):
        bing_videos.supported_languages = ['fr-FR', 'en-US']
        bing_videos.language_aliases = {}
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr-FR'
        dicto['safesearch'] = 0
        dicto['time_range'] = ''
        params = bing_videos.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('bing.com' in params['url'])
        self.assertTrue('SRCHHPGUSR' in params['cookies'])
        self.assertTrue('OFF' in params['cookies']['SRCHHPGUSR'])
        self.assertTrue('_EDGE_S' in params['cookies'])
        self.assertTrue('fr-fr' in params['cookies']['_EDGE_S'])

        dicto['pageno'] = 2
        dicto['time_range'] = 'day'
        dicto['safesearch'] = 2
        params = bing_videos.request(query, dicto)
        self.assertTrue('first=29' in params['url'])
        self.assertTrue('1440' in params['url'])
        self.assertIn('SRCHHPGUSR', params['cookies'])
        self.assertTrue('STRICT' in params['cookies']['SRCHHPGUSR'])

    def test_response(self):
        self.assertRaises(AttributeError, bing_videos.response, None)
        self.assertRaises(AttributeError, bing_videos.response, [])
        self.assertRaises(AttributeError, bing_videos.response, '')
        self.assertRaises(AttributeError, bing_videos.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(bing_videos.response(response), [])

        response = mock.Mock(text='<html></html>')
        self.assertEqual(bing_videos.response(response), [])

        html = """
        <div class="dg_u">
            <div>
                <a>
                    <div>
                        <div>
                            <div class="mc_vtvc_meta_block">
                                <div><span>100 views</span><span>1 year ago</span></div><div><span>ExampleTube</span><span>Channel 1<span></div> #noqa
                            </div>
                        </div>
                        <div class="vrhdata" vrhm='{"du":"01:11","murl":"https://www.example.com/watch?v=DEADBEEF","thid":"OVP.BINGTHUMB1","vt":"Title 1"}'></div> # noqa
                    </div>
                </a>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = bing_videos.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title 1')
        self.assertEqual(results[0]['url'], 'https://www.example.com/watch?v=DEADBEEF')
        self.assertEqual(results[0]['content'], '01:11 - 100 views - 1 year ago - ExampleTube - Channel 1')
        self.assertEqual(results[0]['thumbnail'], 'https://www.bing.com/th?id=OVP.BINGTHUMB1')
