# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import bing_videos
from searx.testing import SearxTestCase


class TestBingVideosEngine(SearxTestCase):

    def test_request(self):
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
        self.assertTrue('first=11' in params['url'])
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
        <div>
            <div class="dg_u">
                <a class="dv_i" href="/videos/search?abcde">
                    <div class="vthblock">
                        <div class="vthumb">
                            <img src="thumb_1.jpg" />
                        </div>
                        <div>
                            <div class="tl">
                                Title 1
                            </div>
                        </div>
                    </div>
                    <div class="videoInfoPanel">
                        <div class="pubInfo">
                            <div>Content 1</div>
                        </div>
                    </div>
                </a>
                <div class="sa_wrapper"
                    data-eventpayload="{&quot;purl&quot;: &quot;https://url.com/1&quot;}">
                </div>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = bing_videos.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title 1')
        self.assertEqual(results[0]['url'], 'https://url.com/1')
        self.assertEqual(results[0]['content'], 'Content 1')
        self.assertEqual(results[0]['thumbnail'], 'thumb_1.jpg')

        html = """
        <div>
            <div class="dg_u">
                <a class="dv_i" href="https://url.com/1">
                    <div class="vthblock">
                        <div class="vthumb">
                            <img src="thumb_1.jpg" />
                        </div>
                        <div>
                            <div class="tl">
                                Title 1
                            </div>
                        </div>
                    </div>
                    <div class="videoInfoPanel">
                        <div class="pubInfo">
                            <div>Content 1</div>
                        </div>
                    </div>
                </a>
            </div>
            <div class="dg_u">
                <a class="dv_i" href="/videos/search?abcde">
                    <div class="vthblock">
                        <div class="vthumb">
                            <img src="thumb_2.jpg" />
                        </div>
                        <div>
                            <div class="tl">
                                Title 2
                            </div>
                        </div>
                    </div>
                    <div class="videoInfoPanel">
                        <div class="pubInfo">
                            <div>Content 2</div>
                        </div>
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
        self.assertEqual(results[0]['url'], 'https://url.com/1')
        self.assertEqual(results[0]['content'], 'Content 1')
        self.assertEqual(results[0]['thumbnail'], 'thumb_1.jpg')
