# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import seedpeer
from searx.testing import SearxTestCase


class TestBtdiggEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = seedpeer.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('seedpeer', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, seedpeer.response, None)
        self.assertRaises(AttributeError, seedpeer.response, [])
        self.assertRaises(AttributeError, seedpeer.response, '')
        self.assertRaises(AttributeError, seedpeer.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(seedpeer.response(response), [])

        html = u"""
        <html>
        <head>
            <script></script>
            <script type="text/javascript" src="not_here.js"></script>
            <script type="text/javascript">
                window.initialData=
                {"data": {"list": [{"name": "Title", "seeds": "10", "peers": "20", "size": "1024", "hash": "abc123"}]}}
            </script>
        </head>
        <body>
            <table></table>
            <table>
                <thead><tr></tr></thead>
                <tbody>
                    <tr>
                        <td><a href="link">Title</a></td>
                        <td>1 year</td>
                        <td>1 KB</td>
                        <td>10</td>
                        <td>20</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        response = mock.Mock(text=html)
        results = seedpeer.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'https://seedpeer.me/link')
        self.assertEqual(results[0]['seed'], 10)
        self.assertEqual(results[0]['leech'], 20)
        self.assertEqual(results[0]['filesize'], 1024)
        self.assertEqual(results[0]['torrentfile'], 'https://seedpeer.me/torrent/abc123')
        self.assertEqual(results[0]['magnetlink'], 'magnet:?xt=urn:btih:abc123')
