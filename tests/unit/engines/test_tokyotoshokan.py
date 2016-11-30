import mock
from collections import defaultdict
from searx.engines import tokyotoshokan
from searx.testing import SearxTestCase
from datetime import datetime


class TestTokyotoshokanEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dic = defaultdict(dict)
        dic['pageno'] = 1
        params = tokyotoshokan.request(query, dic)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('tokyotosho.info' in params['url'])

    def test_response(self):
        resp = mock.Mock(text='<html></html>')
        self.assertEqual(tokyotoshokan.response(resp), [])

        html = """
        <table class="listing">
          <tbody>
            <tr class="shade category_0">
              <td rowspan="2">
                <a href="/?cat=7"><span class="sprite_cat-raw"></span></a>
              </td>
              <td class="desc-top">
                <a href="magnet:?xt=urn:btih:4c19eb46b5113685fbd2288ed2531b0b">
                  <span class="sprite_magnet"></span>
                </a>
                <a rel="nofollow" type="application/x-bittorrent" href="http://www.nyaa.se/f">
                  Koyomimonogatari
                </a>
              </td>
              <td class="web"><a rel="nofollow" href="details.php?id=975700">Details</a></td>
            </tr>
            <tr class="shade category_0">
              <td class="desc-bot">
                Authorized: <span class="auth_ok">Yes</span>
                Submitter: <a href="?username=Ohys">Ohys</a> |
                Size: 10.5MB |
                Date: 2016-03-26 16:41 UTC |
                Comment: sample comment
              </td>
              <td style="color: #BBB; font-family: monospace" class="stats" align="right">
                S: <span style="color: red">53</span>
                L: <span style="color: red">18</span>
                C: <span style="color: red">0</span>
                ID: 975700
              </td>
            </tr>

            <tr class="category_0">
              <td rowspan="2">
                <a href="/?cat=7"><span class="sprite_cat-raw"></span></a>
              </td>
              <td class="desc-top">
                <a rel="nofollow" type="application/x-bittorrent" href="http://google.com/q">
                  Owarimonogatari
                </a>
              </td>
              <td class="web"><a rel="nofollow" href="details.php?id=975700">Details</a></td>
            </tr>
            <tr class="category_0">
              <td class="desc-bot">
                Submitter: <a href="?username=Ohys">Ohys</a> |
                Size: 932.84EB |
                Date: QWERTY-03-26 16:41 UTC
              </td>
              <td style="color: #BBB; font-family: monospace" class="stats" align="right">
                S: <span style="color: red">0</span>
              </td>
            </tr>
          </tbody>
        </table>
        """

        resp = mock.Mock(text=html)
        results = tokyotoshokan.response(resp)

        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)

        # testing the first result, which has correct format
        # and should have all information fields filled
        r = results[0]
        self.assertEqual(r['url'], 'http://www.nyaa.se/f')
        self.assertEqual(r['title'], 'Koyomimonogatari')
        self.assertEqual(r['magnetlink'], 'magnet:?xt=urn:btih:4c19eb46b5113685fbd2288ed2531b0b')
        self.assertEqual(r['filesize'], int(1024 * 1024 * 10.5))
        self.assertEqual(r['publishedDate'], datetime(2016, 3, 26, 16, 41))
        self.assertEqual(r['content'], 'Comment: sample comment')
        self.assertEqual(r['seed'], 53)
        self.assertEqual(r['leech'], 18)

        # testing the second result, which does not include magnet link,
        # seed & leech info, and has incorrect size & creation date
        r = results[1]
        self.assertEqual(r['url'], 'http://google.com/q')
        self.assertEqual(r['title'], 'Owarimonogatari')

        self.assertFalse('magnetlink' in r)
        self.assertFalse('filesize' in r)
        self.assertFalse('content' in r)
        self.assertFalse('publishedDate' in r)
        self.assertFalse('seed' in r)
        self.assertFalse('leech' in r)
