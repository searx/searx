# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import www1337x
from searx.testing import SearxTestCase


class Test1337xEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['category'] = 'videos'
        params = www1337x.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('1337x.to', params['url'])
        self.assertIn('1', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, www1337x.response, None)
        self.assertRaises(AttributeError, www1337x.response, [])
        self.assertRaises(AttributeError, www1337x.response, '')
        self.assertRaises(AttributeError, www1337x.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(www1337x.response(response), [])

        html = """
        <table class="table-list table table-responsive table-striped">
<thead>
<tr>
<th class="coll-1 name">name</th>
<th class="coll-2">se</th>
<th class="coll-3">le</th>
<th class="coll-date">time</th>
<th class="coll-4"><span class="size">size</span></th>
<th class="coll-5">uploader</th>
</tr>
</thead>
<tbody>
<tr>
<td class="name"><a></a><a href="/torrent/link/">Pirates</a></td>
<td class="coll-2 seeds">15454</td>
<td class="coll-3 leeches">7968</td>
<td class="coll-date">Sep. 5th '17</td>
<td class="coll-4 size mob-uploader">4.4 GB</td>
<td class="coll-5 uploader"><a href="/user/Cristie/">Cristie</a></td>
</tr>
<tr>
<td class="name"><a></a><a href="/torrent/link/">Pirates2</a></td>
<td class="coll-2 seeds">10490</td>
<td class="coll-3 leeches">5304</td>
<td class="coll-date">Sep. 11th '17</td>
<td class="coll-4 size mob-uploader">2.0 GB</td>
<td class="coll-5 uploader"><a href="/user/YTSAGx/">YTSAGx</a></td>
</tr>
</tbody>
</table>
        """
        response = mock.Mock(text=html)
        results = www1337x.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(
            results[0]['title'],
            'Pirates')
        self.assertEqual(
            results[0]['url'],
            'https://1337x.to/torrent/link/')
        self.assertEqual(results[0]['seed'], '15454')
        self.assertEqual(results[0]['leech'], '7968')
        self.assertEqual(results[0]['filesize'], 4724464025)

        html = """
        <table class="table-list">
        </table>
        """
        response = mock.Mock(text=html)
        results = www1337x.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
