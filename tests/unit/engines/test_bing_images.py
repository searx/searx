# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import bing_images
from searx.testing import SearxTestCase


class TestBingImagesEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        dicto['safesearch'] = 1
        dicto['time_range'] = ''
        params = bing_images.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('bing.com' in params['url'])
        self.assertTrue('SRCHHPGUSR' in params['cookies'])
        self.assertTrue('fr' in params['cookies']['SRCHHPGUSR'])

        dicto['language'] = 'all'
        params = bing_images.request(query, dicto)
        self.assertIn('SRCHHPGUSR', params['cookies'])
        self.assertIn('en', params['cookies']['SRCHHPGUSR'])

    def test_response(self):
        self.assertRaises(AttributeError, bing_images.response, None)
        self.assertRaises(AttributeError, bing_images.response, [])
        self.assertRaises(AttributeError, bing_images.response, '')
        self.assertRaises(AttributeError, bing_images.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(bing_images.response(response), [])

        response = mock.Mock(text='<html></html>')
        self.assertEqual(bing_images.response(response), [])

        html = """
        <div id="mmComponent_images_1">
            <ul>
                <li>
                    <div>
                        <div class="imgpt">
                            <a m='{"purl":"page_url","murl":"img_url"}' mad='{"turl":"thumb_url"}'>
                                <img src="" alt="alt text" />
                            </a>
                        </div>
                        <div></div>
                    </div>
                    <div>
                        <div class="imgpt">
                            <a m='{"purl":"page_url2","murl":"img_url2"}' mad='{"turl":"thumb_url2"}'>
                                <img src="" alt="alt text 2" />
                            </a>
                        </div>
                    </div>
                </li>
            </ul>
            <ul>
                <li>
                    <div>
                        <div class="imgpt">
                            <a m='{"purl":"page_url3","murl":"img_url3"}' mad='{"turl":"thumb_url3"}'>
                                <img src="" alt="alt text 3" />
                            </a>
                        </div>
                    </div>
                </li>
            </ul>
        </div>
        """
        html = html.replace('\r\n', '').replace('\n', '').replace('\r', '')
        response = mock.Mock(text=html)
        results = bing_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'alt text')
        self.assertEqual(results[0]['url'], 'page_url')
        self.assertEqual(results[0]['content'], '')
        self.assertEqual(results[0]['thumbnail_src'], 'thumb_url')
        self.assertEqual(results[0]['img_src'], 'img_url')
