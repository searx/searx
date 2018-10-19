import mock
from collections import defaultdict
from searx.engines import torrentz
from searx.testing import SearxTestCase
from datetime import datetime


class TestTorrentzEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dic = defaultdict(dict)
        dic['pageno'] = 1
        params = torrentz.request(query, dic)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('torrentz2.eu' in params['url'])

    def test_response(self):
        resp = mock.Mock(text='<html></html>')
        self.assertEqual(torrentz.response(resp), [])

        html = """
        <div class="results">
          <dl>
            <dt>
              <a href="/4362e08b1d80e1820fb2550b752f9f3126fe76d6">
                Completely valid info
              </a>
              books ebooks
            </dt>
            <dd>
              <span>1</span>
              <span title="1503595924">5 hours</span>
              <span>30 MB</span>
              <span>14</span>
              <span>1</span>
            </dd>
          </dl>

          <dl>
            <dt>
              <a href="/poaskdpokaspod">
                Invalid hash and date and filesize
              </a>
              books ebooks
            </dt>
            <dd>
              <span>1</span>
              <span title="1503595924 aaa">5 hours</span>
              <span>30MB</span>
              <span>5,555</span>
              <span>1,234,567</span>
            </dd>
          </dl>
        </div>
        """

        resp = mock.Mock(text=html)
        results = torrentz.response(resp)

        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)

        # testing against the first result
        r = results[0]
        self.assertEqual(r['url'], 'https://torrentz2.eu/4362e08b1d80e1820fb2550b752f9f3126fe76d6')
        self.assertEqual(r['title'], 'Completely valid info books ebooks')
        # 22 Nov 2015 03:01:42
        self.assertEqual(r['publishedDate'], datetime.fromtimestamp(1503595924))
        self.assertEqual(r['seed'], 14)
        self.assertEqual(r['leech'], 1)
        self.assertEqual(r['filesize'], 30 * 1024 * 1024)
        self.assertEqual(r['magnetlink'], 'magnet:?xt=urn:btih:4362e08b1d80e1820fb2550b752f9f3126fe76d6')

        # testing against the second result
        r = results[1]
        self.assertEqual(r['url'], 'https://torrentz2.eu/poaskdpokaspod')
        self.assertEqual(r['title'], 'Invalid hash and date and filesize books ebooks')
        self.assertEqual(r['seed'], 5555)
        self.assertEqual(r['leech'], 1234567)

        # in the second result we have invalid hash, creation date & torrent size,
        # so these tests should fail
        self.assertFalse('magnetlink' in r)
        self.assertFalse('filesize' in r)
        self.assertFalse('publishedDate' in r)
