from collections import defaultdict
import mock
from searx.engines import nyaa
from searx.testing import SearxTestCase


class TestNyaaEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dic = defaultdict(dict)
        dic['pageno'] = 1
        params = nyaa.request(query, dic)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('nyaa.se' in params['url'])

    def test_response(self):
        resp = mock.Mock(text='<html></html>')
        self.assertEqual(nyaa.response(resp), [])

        html = """
        <table class="tlist">
          <tbody>
            <tr class="trusted tlistrow">
              <td class="tlisticon">
                <a href="//www.nyaa.se" title="English-translated Anime">
                   <img src="//files.nyaa.se" alt="English-translated Anime">
                </a>
              </td>
              <td class="tlistname">
                <a href="//www.nyaa.se/?page3">
                  Sample torrent title
                </a>
              </td>
              <td class="tlistdownload">
                <a href="//www.nyaa.se/?page_dl" title="Download">
                  <img src="//files.nyaa.se/www-dl.png" alt="DL">
                </a>
              </td>
              <td class="tlistsize">10 MiB</td>
              <td class="tlistsn">1</td>
              <td class="tlistln">3</td>
              <td class="tlistdn">666</td>
              <td class="tlistmn">0</td>
            </tr>
          </tbody>
        </table>
        """

        resp = mock.Mock(text=html)
        results = nyaa.response(resp)

        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)

        r = results[0]
        self.assertTrue(r['url'].find('www.nyaa.se/?page3') >= 0)
        self.assertTrue(r['torrentfile'].find('www.nyaa.se/?page_dl') >= 0)
        self.assertTrue(r['content'].find('English-translated Anime') >= 0)
        self.assertTrue(r['content'].find('Downloaded 666 times.') >= 0)

        self.assertEqual(r['title'], 'Sample torrent title')
        self.assertEqual(r['seed'], 1)
        self.assertEqual(r['leech'], 3)
        self.assertEqual(r['filesize'], 10 * 1024 * 1024)
