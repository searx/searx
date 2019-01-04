# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import bing_images
from searx.testing import SearxTestCase


class TestBingImagesEngine(SearxTestCase):

    def test_request(self):
        bing_images.supported_languages = ['fr-FR', 'en-US']
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr-FR'
        dicto['safesearch'] = 1
        dicto['time_range'] = ''
        params = bing_images.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('bing.com' in params['url'])
        self.assertTrue('SRCHHPGUSR' in params['cookies'])
        self.assertTrue('DEMOTE' in params['cookies']['SRCHHPGUSR'])
        self.assertTrue('_EDGE_S' in params['cookies'])
        self.assertTrue('fr-fr' in params['cookies']['_EDGE_S'])

        dicto['language'] = 'fr'
        params = bing_images.request(query, dicto)
        self.assertTrue('_EDGE_S' in params['cookies'])
        self.assertTrue('fr-fr' in params['cookies']['_EDGE_S'])

        dicto['language'] = 'all'
        params = bing_images.request(query, dicto)
        self.assertTrue('_EDGE_S' in params['cookies'])
        self.assertTrue('en-us' in params['cookies']['_EDGE_S'])

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
                            <a m='{"purl":"page_url","murl":"img_url","turl":"thumb_url"}'>
                                <img src="" alt="alt text" />
                            </a>
                        </div>
                        <div></div>
                    </div>
                    <div>
                        <div class="imgpt">
                            <a m='{"purl":"page_url2","murl":"img_url2","turl":"thumb_url2"}'>
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
                            <a m='{"purl":"page_url3","murl":"img_url3","turl":"thumb_url3"}'>
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

    def test_fetch_supported_languages(self):
        html = """
        <div>
            <div id="region-section-content">
                <ul class="b_vList">
                    <li>
                        <a href="https://bing...&setmkt=de-DE&s...">Germany</a>
                        <a href="https://bing...&setmkt=nb-NO&s...">Norway</a>
                    </li>
                </ul>
                <ul class="b_vList">
                    <li>
                        <a href="https://bing...&setmkt=es-AR&s...">Argentina</a>
                    </li>
                </ul>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        languages = list(bing_images._fetch_supported_languages(response))
        self.assertEqual(len(languages), 3)
        self.assertIn('de-DE', languages)
        self.assertIn('no-NO', languages)
        self.assertIn('es-AR', languages)
