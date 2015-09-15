# -*- coding: utf-8 -*-
import mock
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

    def test_highlight_content(self):
        self.assertEqual(utils.highlight_content(0, None), None)
        self.assertEqual(utils.highlight_content(None, None), None)
        self.assertEqual(utils.highlight_content('', None), None)
        self.assertEqual(utils.highlight_content(False, None), None)

        contents = [
            '<html></html>'
            'not<'
        ]
        for content in contents:
            self.assertEqual(utils.highlight_content(content, None), content)

        content = 'a'
        query = 'test'
        self.assertEqual(utils.highlight_content(content, query), content)
        query = 'a test'
        self.assertEqual(utils.highlight_content(content, query), content)

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
        self.assertIsInstance(utils.html_to_text(html), unicode)
        self.assertIsNotNone(utils.html_to_text(html))
        self.assertEqual(utils.html_to_text(html), "Test text")

    def test_prettify_url(self):
        data = (('https://searx.me/', 'https://searx.me/'),
                (u'https://searx.me/ű', u'https://searx.me/ű'),
                ('https://searx.me/' + (100 * 'a'), 'https://searx.me/[...]aaaaaaaaaaaaaaaaa'),
                (u'https://searx.me/' + (100 * u'ű'), u'https://searx.me/[...]űűűűűűűűűűűűűűűűű'))

        for test_url, expected in data:
            self.assertEqual(utils.prettify_url(test_url, max_length=32), expected)


class TestHTMLTextExtractor(SearxTestCase):

    def setUp(self):
        self.html_text_extractor = utils.HTMLTextExtractor()

    def test__init__(self):
        self.assertEqual(self.html_text_extractor.result, [])

    def test_handle_charref(self):
        self.html_text_extractor.handle_charref('xF')
        self.assertIn(u'\x0f', self.html_text_extractor.result)
        self.html_text_extractor.handle_charref('XF')
        self.assertIn(u'\x0f', self.html_text_extractor.result)

        self.html_text_extractor.handle_charref('97')
        self.assertIn(u'a', self.html_text_extractor.result)

    def test_handle_entityref(self):
        entity = 'test'
        self.html_text_extractor.handle_entityref(entity)
        self.assertIn(entity, self.html_text_extractor.result)


class TestUnicodeWriter(SearxTestCase):

    def setUp(self):
        self.unicode_writer = utils.UnicodeWriter(mock.MagicMock())

    def test_write_row(self):
        row = [1, 2, 3]
        self.assertEqual(self.unicode_writer.writerow(row), None)

    def test_write_rows(self):
        self.unicode_writer.writerow = mock.MagicMock()
        rows = [1, 2, 3]
        self.unicode_writer.writerows(rows)
        self.assertEqual(self.unicode_writer.writerow.call_count, len(rows))


class TestFormParser(SearxTestCase):
    def test_empty_form(self):
        self.assertEqual(len(list(utils.parse_form([]))), 1)
        self.assertIn("allowed_plugins", utils.parse_form([]))
        self.assertGreater(len(utils.parse_form([])["allowed_plugins"]), 0)

    def test_single_items_only(self):
        results = utils.parse_form([
            ("name", "John Doe"),
            ("website", "example.com"),
            ("age", "34"),
        ])
        self.assertEqual(len(results), 4)
        self.assertEqual(results["name"], "John Doe")
        self.assertEqual(results["age"], "34")

    def test_disabling_plugins(self):
        results = utils.parse_form([
            ("name", "John Doe"),
            ("website", "example.com"),
            ("age", "34"),
            ("plugin_Tracker_URL_remover", "plugin_Tracker_URL_remover"),
        ])
        self.assertIn("disabled_plugins", results)
        self.assertIn("allowed_plugins", results)
        self.assertEqual(results["disabled_plugins"], {"Tracker_URL_remover", })

    def test_collection_items(self):
        results = utils.parse_form([
            ("name", "John Doe"),
            ("website", "example.com"),
            ("age", "34"),
            ("child_Clair", "x"),
            ("child_Adam", "x"),
        ], collection_fields={"child": "children"})
        self.assertEqual(len(results["children"]), 2)
        self.assertIn("Clair", results["children"])
        self.assertIn("Adam", results["children"])
        self.assertNotIn("Jane", results["children"])

    def test_underscore_in_non_collection_name(self):
        results = utils.parse_form([
            ("name", "John Doe"),
            ("website", "example.com"),
            ("age", "34"),
            ("children_Clair", "x"),
            ("children_Adam", "x"),
        ])
        self.assertNotIn("children", results.keys())
        self.assertIn("children_Clair", results.keys())

    def test_collection_items_is_of_type_set(self):
        results = utils.parse_form([
            ("name", "John Doe"),
            ("website", "example.com"),
            ("age", "34"),
            ("child_Clair", "x"),
            ("child_Adam", "x"),
        ], collection_fields={"child": "children"})
        self.assertTrue(isinstance(results["children"], set))
