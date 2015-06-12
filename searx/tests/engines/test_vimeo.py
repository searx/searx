# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import vimeo
from searx.testing import SearxTestCase


class TestVimeoEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = vimeo.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('vimeo.com' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, vimeo.response, None)
        self.assertRaises(AttributeError, vimeo.response, [])
        self.assertRaises(AttributeError, vimeo.response, '')
        self.assertRaises(AttributeError, vimeo.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(vimeo.response(response), [])

        html = """
        <div id="browse_content" class="results_grid" data-search-id="696d5f8366914ec4ffec33cf7652de384976d4f4">
            <ul class="js-browse_list clearfix browse browse_videos browse_videos_thumbnails kane"
                data-stream="c2VhcmNoOjo6ZGVzYzp7InF1ZXJ5IjoidGVzdCJ9">
                <li data-position="7" data-result-id="clip_79600943">
                    <div class="clip_thumbnail">
                        <a href="/videoid" class="js-result_url">
                            <div class="thumbnail_wrapper">
                                <img src="http://image.url.webp" class="js-clip_thumbnail_image">
                                <div class="overlay overlay_clip_meta">
                                    <div class="meta_data_footer">
                                        <span class="clip_upload_date">
                                            <time datetime="2013-11-17T08:49:09-05:00"
                                                title="dimanche 17 novembre 2013 08:49">Il y a 1 an</time>
                                        </span>
                                        <span class="clip_likes">
                                            <img src="https://f.vimeocdn.com/images_v6/svg/heart-icon.svg">2 215
                                        </span>
                                        <span class="clip_comments">
                                            <img src="https://f.vimeocdn.com/images_v6/svg/comment-icon.svg">75
                                        </span>
                                        <span class="overlay meta_data_footer clip_duration">01:12</span>
                                    </div>
                                </div>
                            </div>
                            <span class="title">This is the title</span>
                        </a>
                    </div>
                    <div class="clip_thumbnail_attribution">
                        <a href="/fedorshmidt">
                            <img src="https://i.vimeocdn.com/portrait/6628061_100x100.jpg" class="avatar">
                            <span class="display_name">Fedor Shmidt</span>
                        </a>
                        <span class="plays">2,1M lectures</span>
                    </div>
                </li>
            </ul>
        </div>
        """
        response = mock.Mock(text=html)
        results = vimeo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://vimeo.com/videoid')
        self.assertEqual(results[0]['content'], '')
        self.assertEqual(results[0]['thumbnail'], 'http://image.url.webp')
        self.assertIn('/videoid', results[0]['embedded'])

        html = """
        <ol class="js-browse_list clearfix browse browse_videos browse_videos_thumbnails kane"
            data-stream="c2VhcmNoOjo6ZGVzYzp7InF1ZXJ5IjoidGVzdCJ9">
            <li id="clip_100785455" data-start-page="/search/page:1/sort:relevant/" data-position="1">
                <a href="/videoid" title="Futurama 3d (test shot)">
                    <img src="http://image.url.webp"
                        srcset="http://i.vimeocdn.com/video/482375085_590x332.webp 2x" alt=""
                        class="thumbnail thumbnail_lg_wide">
                    <div class="data">
                        <p class="title">
                            This is the title
                        </p>
                        <p class="meta">
                            <time datetime="2014-07-15T04:16:27-04:00"
                                title="mardi 15 juillet 2014 04:16">Il y a 6 mois</time>
                        </p>
                    </div>
                </a>
            </li>
        </ol>
        """
        response = mock.Mock(text=html)
        results = vimeo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
