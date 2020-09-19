# -*- coding: utf-8 -*-
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
        html = """
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
        self.assertIsInstance(utils.html_to_text(html), str)
        self.assertIsNotNone(utils.html_to_text(html))
        self.assertEqual(utils.html_to_text(html), "Test text")

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
