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
        <div id="browse_content" class="" data-search-id="696d5f8366914ec4ffec33cf7652de384976d4f4">
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
