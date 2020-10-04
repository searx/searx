# -*- coding: utf-8 -*-
import lxml.etree
from lxml import html

from searx.testing import SearxTestCase
from searx import utils


class TestUtils(SearxTestCase):

    def test_gen_useragent(self):
        self.assertIsInstance(utils.gen_useragent(), str)
        self.assertIsNotNone(utils.gen_useragent())
        self.assertTrue(utils.gen_useragent().startswith('Mozilla'))

    def test_searx_useragent(self):
        self.assertIsInstance(utils.searx_useragent(), str)
        self.assertIsNotNone(utils.searx_useragent())
        self.assertTrue(utils.searx_useragent().startswith('searx'))

    def test_html_to_text(self):
        html_str = """
        <a href="/testlink" class="link_access_account">
            <style>
                .toto {
                    color: red;
                }
            </style>
            <span class="toto">
                <span>
                    <img src="test.jpg" />
                </span>
            </span>
            <span class="titi">
                            Test text
            </span>
            <script>value='dummy';</script>
        </a>
        """
        self.assertIsInstance(utils.html_to_text(html_str), str)
        self.assertIsNotNone(utils.html_to_text(html_str))
        self.assertEqual(utils.html_to_text(html_str), "Test text")

    def test_extract_text(self):
        html_str = """
        <a href="/testlink" class="link_access_account">
            <span class="toto">
                <span>
                    <img src="test.jpg" />
                </span>
            </span>
            <span class="titi">
                            Test text
            </span>
        </a>
        """
        dom = html.fromstring(html_str)
        self.assertEqual(utils.extract_text(dom), 'Test text')
        self.assertEqual(utils.extract_text(dom.xpath('//span')), 'Test text')
        self.assertEqual(utils.extract_text(dom.xpath('//img/@src')), 'test.jpg')
        self.assertEqual(utils.extract_text(dom.xpath('//unexistingtag')), '')

    def test_extract_url(self):
        def f(html_str, search_url):
            return utils.extract_url(html.fromstring(html_str), search_url)
        self.assertEqual(f('<span id="42">https://example.com</span>', 'http://example.com/'), 'https://example.com/')
        self.assertEqual(f('https://example.com', 'http://example.com/'), 'https://example.com/')
        self.assertEqual(f('//example.com', 'http://example.com/'), 'http://example.com/')
        self.assertEqual(f('//example.com', 'https://example.com/'), 'https://example.com/')
        self.assertEqual(f('/path?a=1', 'https://example.com'), 'https://example.com/path?a=1')
        with self.assertRaises(lxml.etree.ParserError):
            f('', 'https://example.com')
        with self.assertRaises(Exception):
            utils.extract_url([], 'https://example.com')

    def test_html_to_text_invalid(self):
        html = '<p><b>Lorem ipsum</i>dolor sit amet</p>'
        self.assertEqual(utils.html_to_text(html), "Lorem ipsum")

    def test_match_language(self):
        self.assertEqual(utils.match_language('es', ['es']), 'es')
        self.assertEqual(utils.match_language('es', [], fallback='fallback'), 'fallback')
        self.assertEqual(utils.match_language('ja', ['jp'], {'ja': 'jp'}), 'jp')

        aliases = {'en-GB': 'en-UK', 'he': 'iw'}

        # guess country
        self.assertEqual(utils.match_language('de-DE', ['de']), 'de')
        self.assertEqual(utils.match_language('de', ['de-DE']), 'de-DE')
        self.assertEqual(utils.match_language('es-CO', ['es-AR', 'es-ES', 'es-MX']), 'es-ES')
        self.assertEqual(utils.match_language('es-CO', ['es-MX']), 'es-MX')
        self.assertEqual(utils.match_language('en-UK', ['en-AU', 'en-GB', 'en-US']), 'en-GB')
        self.assertEqual(utils.match_language('en-GB', ['en-AU', 'en-UK', 'en-US'], aliases), 'en-UK')

        # language aliases
        self.assertEqual(utils.match_language('iw', ['he']), 'he')
        self.assertEqual(utils.match_language('he', ['iw'], aliases), 'iw')
        self.assertEqual(utils.match_language('iw-IL', ['he']), 'he')
        self.assertEqual(utils.match_language('he-IL', ['iw'], aliases), 'iw')
        self.assertEqual(utils.match_language('iw', ['he-IL']), 'he-IL')
        self.assertEqual(utils.match_language('he', ['iw-IL'], aliases), 'iw-IL')
        self.assertEqual(utils.match_language('iw-IL', ['he-IL']), 'he-IL')
        self.assertEqual(utils.match_language('he-IL', ['iw-IL'], aliases), 'iw-IL')

    def test_ecma_unscape(self):
        self.assertEqual(utils.ecma_unescape('text%20with%20space'), 'text with space')
        self.assertEqual(utils.ecma_unescape('text using %xx: %F3'),
                         u'text using %xx: ó')
        self.assertEqual(utils.ecma_unescape('text using %u: %u5409, %u4E16%u754c'),
                         u'text using %u: 吉, 世界')


class TestHTMLTextExtractor(SearxTestCase):

    def setUp(self):
        self.html_text_extractor = utils.HTMLTextExtractor()

    def test__init__(self):
        self.assertEqual(self.html_text_extractor.result, [])

    def test_handle_charref(self):
        self.html_text_extractor.handle_charref('xF')
        self.assertIn('\x0f', self.html_text_extractor.result)
        self.html_text_extractor.handle_charref('XF')
        self.assertIn('\x0f', self.html_text_extractor.result)

        self.html_text_extractor.handle_charref('97')
        self.assertIn('a', self.html_text_extractor.result)

    def test_handle_entityref(self):
        entity = 'test'
        self.html_text_extractor.handle_entityref(entity)
        self.assertIn(entity, self.html_text_extractor.result)

    def test_invalid_html(self):
        text = '<p><b>Lorem ipsum</i>dolor sit amet</p>'
        with self.assertRaises(utils.HTMLTextExtractorException):
            self.html_text_extractor.feed(text)
