from collections import defaultdict
import mock
from searx.engines import horriblesubs
from searx.testing import SearxTestCase


class TestHorribleSubsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dic = defaultdict(dict)
        dic['pageno'] = 0
        params = horriblesubs.request(query, dic)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('horriblesubs.info' in params['url'])

    def test_response(self):
        resp = mock.Mock(text='<html></html>', url='http://horriblesubs.info/lib/search.php?value=test&offset=0',
                         search_params={'pageno': 1})
        self.assertEqual(horriblesubs.response(resp), [])

        html = """
        <div class="release-links some-kind-of-title-480p">
            <table class="release-table" cellpadding="0" border="0" cellspacing="0">
                <tr>
                    <td class="dl-label"><i>Some kind of title [480p]</i>
                    </td>
                    <td class="dl-type hs-magnet-link">
                        <span class="dl-link"><a title="Magnet Link" href="magnet.link">Magnet</a></span>
                    </td>
                    <td class="dl-type hs-torrent-link">
                        <span class="dl-link"><a title="Torrent Link"
                            href="http://www.nyaa.se/?page=download&tid=sometestid">Torrent</a></span>
                    </td>
                    <td class="dl-type hs-ddl-link">
                        <span class="dl-link"><a title="Download from FileFactory" href="ffddl.link">FF</a></span>
                    </td>
                    <td class="dl-type hs-ddl-link">
                        <span class="dl-link"><a title="Download from Uploaded.net" href="ulddl.link">UL</a></span>
                    </td>
                    <td class="linkless dl-type hs-ddl-link">MXS</td>
                    <td class="dl-type hs-ddl-link">
                        <span class="dl-link"><a title="Download from UploadRocket.net" href="urddl.link">UR</a></span>
                    </td>
                </tr>
            </table>
        </div>
        """

        resp = mock.Mock(text=html, url='http://horriblesubs.info/lib/search.php?value=test&offset=0',
                         search_params={'pageno': 1})
        results = horriblesubs.response(resp)

        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)

        r = results[0]
        self.assertEqual(r['url'], 'http://www.nyaa.se/?page=view&tid=sometestid')
        self.assertEqual(r['title'], 'Some kind of title [480p]')
        self.assertEqual(r['content'], 'Resolution: 480p')
        self.assertEqual(r['magnetlink'], 'magnet.link')
        self.assertEqual(r['torrentfile'], 'http://www.nyaa.se/?page=download&tid=sometestid')
        self.assertEqual(r['ddls'][0]['url'], 'ffddl.link')
        self.assertEqual(r['ddls'][0]['title'], 'FF')
