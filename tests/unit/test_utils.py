# -*- coding: utf-8 -*-
import os
import tempfile
import stat

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


class TestSecretAppKey(SearxTestCase):

    def setUp(self):
        self.getkey = utils.get_secret_app_key
        self.fn = utils._secret_app_key_file_name

    def keyfile(self, dir_):
        return os.path.join(dir_, self.fn)

    @staticmethod
    def freshdir():
        return tempfile.mkdtemp()

    # generation of a key
    def test_empty_dir(self):
        dir_ = self.freshdir()
        key = self.getkey(dir_)
        self.assertNotEqual(key, "")
        file_ = self.keyfile(dir_)
        self.assertTrue(os.path.isfile(file_))
        mode = os.stat(file_).st_mode
        # equal to read and write for user
        self.assertEquals(mode & (stat.S_IRWXG | stat.S_IRWXU | stat.S_IRWXO),
                          (stat.S_IRUSR | stat.S_IWUSR))

    # generation & successive read of the generated key
    def test_existing_key(self):
        dir_ = self.freshdir()
        key = self.getkey(dir_)
        key2 = self.getkey(dir_)
        self.assertEquals(key, key2)

    def test_not_nice(self):
        def touch(f, mode):
            open(f, 'w').close()
            os.chmod(f, mode)

        def raisesappkeyerror(dir_):
            with self.assertRaises(utils.SecretAppKeyError):
                self.getkey(dir_)

        # input dir doesn't exist
        raisesappkeyerror("<nonexisting file>")

        # read-only
        d1 = self.freshdir()
        touch(self.keyfile(d1), 0)
        raisesappkeyerror(d1)

        # dir
        d2 = self.freshdir()
        os.mkdir(self.keyfile(d2))
        raisesappkeyerror(d2)

        # non-writable dir
        d3 = self.freshdir()
        os.chmod(d3, stat.S_IRUSR)
        raisesappkeyerror(d3)
