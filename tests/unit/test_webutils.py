# -*- coding: utf-8 -*-
import mock
from searx.testing import SearxTestCase
from searx import webutils


class TestWebUtils(SearxTestCase):

    def test_prettify_url(self):
        data = (('https://searx.me/', 'https://searx.me/'),
                ('https://searx.me/ű', 'https://searx.me/ű'),
                ('https://searx.me/' + (100 * 'a'), 'https://searx.me/[...]aaaaaaaaaaaaaaaaa'),
                ('https://searx.me/' + (100 * 'ű'), 'https://searx.me/[...]űűűűűűűűűűűűűűűűű'))

        for test_url, expected in data:
            self.assertEqual(webutils.prettify_url(test_url, max_length=32), expected)

    def test_highlight_content(self):
        self.assertEqual(webutils.highlight_content(0, None), None)
        self.assertEqual(webutils.highlight_content(None, None), None)
        self.assertEqual(webutils.highlight_content('', None), None)
        self.assertEqual(webutils.highlight_content(False, None), None)

        contents = [
            '<html></html>'
            'not<'
        ]
        for content in contents:
            self.assertEqual(webutils.highlight_content(content, None), content)

        content = 'a'
        query = 'test'
        self.assertEqual(webutils.highlight_content(content, query), content)
        query = 'a test'
        self.assertEqual(webutils.highlight_content(content, query), content)


class TestUnicodeWriter(SearxTestCase):

    def setUp(self):
        self.unicode_writer = webutils.UnicodeWriter(mock.MagicMock())

    def test_write_row(self):
        row = [1, 2, 3]
        self.assertEqual(self.unicode_writer.writerow(row), None)

    def test_write_rows(self):
        self.unicode_writer.writerow = mock.MagicMock()
        rows = [1, 2, 3]
        self.unicode_writer.writerows(rows)
        self.assertEqual(self.unicode_writer.writerow.call_count, len(rows))


class TestNewHmac(SearxTestCase):

    def test_bytes(self):
        for secret_key in ['secret', b'secret', 1]:
            if secret_key == 1:
                with self.assertRaises(TypeError):
                    webutils.new_hmac(secret_key, b'http://example.com')
                continue
            res = webutils.new_hmac(secret_key, b'http://example.com')
            self.assertEqual(
                res,
                '23e2baa2404012a5cc8e4a18b4aabf0dde4cb9b56f679ddc0fd6d7c24339d819')
