# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import bing_videos
from searx.testing import SearxTestCase


class TestBingVideosEngine(SearxTestCase):

    def test_request(self):
        bing_videos.supported_languages = ['fr-FR', 'en-US']

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
        <div class="dg_u">
            <div id="mc_vtvc_1" class="mc_vtvc">
                <a class="mc_vtvc_link" href="/video">
                    <div class="mc_vtvc_th">
                        <div class="cico">
                            <img src="thumb_1.jpg" />
                        </div>
                        <div class="mc_vtvc_ban_lo">
                            <div class="vtbc">
                                <div class="mc_bc_w b_smText">
                                    <div class="mc_bc pivot bpi_2">
                                        <span title="">
                                             <span class="mv_vtvc_play cipg "></span>
                                        </span>
                                    </div>
                                    <div class="mc_bc items">10:06</div>
                                </div>
                            </div>
                        </div>
                        </div>
                        <div class="mc_vtvc_meta">
                        <div class="mc_vtvc_title" title="Title 1"></div>
                        <div class="mc_vtvc_meta_block_area">
                        <div class="mc_vtvc_meta_block">
                            <div class="mc_vtvc_meta_row">
                                <span>65,696,000+ views</span>
                                <span>1 year ago</span>
                            </div>
                            <div class="mc_vtvc_meta_row mc_vtvc_meta_row_channel">Content 1</div>
                            <div class="mc_vtvc_meta_row"><span>
                                <div class="cico mc_vtvc_src_ico">
                                    <div></div>
                                </div>
                                <span>YouTube</span>
                            </span></div>
                        </div>
                        </div>
                    </div>
                    <div class="vrhdata"></div>
                    </a>
                </div>
            </div>
        """
        response = mock.Mock(text=html)
        results = bing_videos.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title 1')
        self.assertEqual(results[0]['url'], 'https://bing.com/video')
        self.assertEqual(results[0]['content'], 'Content 1')
        self.assertEqual(results[0]['thumbnail'], 'thumb_1.jpg')
