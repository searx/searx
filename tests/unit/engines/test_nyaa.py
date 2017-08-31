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
        self.assertTrue('nyaa.si' in params['url'])

    def test_response(self):
        resp = mock.Mock(text='<html></html>')
        self.assertEqual(nyaa.response(resp), [])

        html = """
        <table class="table table-bordered table-hover table-striped torrent-list">
        <thead>
        <tr>
        <th class="hdr-category text-center" style="width:80px;">
        <div>Category</div>
        </th>
        <th class="hdr-name" style="width:auto;">
        <div>Name</div>
        </th>
        <th class="hdr-comments sorting text-center" title="Comments" style="width:50px;">
        <a href="/?f=0&amp;c=0_0&amp;q=Death+Parade&amp;s=comments&amp;o=desc"></a>
        <i class="fa fa-comments-o"></i>
        </th>
        <th class="hdr-link text-center" style="width:70px;">
        <div>Link</div>
        </th>
        <th class="hdr-size sorting text-center" style="width:100px;">
        <a href="/?f=0&amp;c=0_0&amp;q=Death+Parade&amp;s=size&amp;o=desc"></a>
        <div>Size</div>
        </th>
        <th class="hdr-date sorting_desc text-center" title="In local time" style="width:140px;">
        <a href="/?f=0&amp;c=0_0&amp;q=Death+Parade&amp;s=id&amp;o=asc"></a>
        <div>Date</div>
        </th>
        <th class="hdr-seeders sorting text-center" title="Seeders" style="width:50px;">
        <a href="/?f=0&amp;c=0_0&amp;q=Death+Parade&amp;s=seeders&amp;o=desc"></a>
        <i class="fa fa-arrow-up" aria-hidden="true"></i>
        </th>
        <th class="hdr-leechers sorting text-center" title="Leechers" style="width:50px;">
        <a href="/?f=0&amp;c=0_0&amp;q=Death+Parade&amp;s=leechers&amp;o=desc"></a>
        <i class="fa fa-arrow-down" aria-hidden="true"></i>
        </th>
        <th class="hdr-downloads sorting text-center" title="Completed downloads" style="width:50px;">
        <a href="/?f=0&amp;c=0_0&amp;q=Death+Parade&amp;s=downloads&amp;o=desc"></a>
        <i class="fa fa-check" aria-hidden="true"></i>
        </th>
        </tr>
        </thead>
        <tbody>
        <tr class="default">
        <td style="padding:0 4px;">
        <a href="/?c=1_2" title="Anime - English-translated">
        <img src="/static/img/icons/nyaa/1_2.png" alt="Anime - English-translated">
        </a>
        </td>
        <td colspan="2">
        <a href="/view/1" title="Sample title 1">Sample title 1</a>
        </td>
        <td class="text-center" style="white-space: nowrap;">
        <a href="/download/1.torrent"><i class="fa fa-fw fa-download"></i></a>
        <a href="magnet:?xt=urn:btih:2"><i class="fa fa-fw fa-magnet"></i></a>
        </td>
        <td class="text-center">723.7 MiB</td>
        <td class="text-center" data-timestamp="1503307456" title="1 week 3
        days 9 hours 44 minutes 39 seconds ago">2017-08-21 11:24</td>
        <td class="text-center" style="color: green;">1</td>
        <td class="text-center" style="color: red;">3</td>
        <td class="text-center">12</td>
        </tr>
        <tr class="default">
        <td style="padding:0 4px;">
        <a href="/?c=1_2" title="Anime - English-translated">
        <img src="/static/img/icons/nyaa/1_2.png" alt="Anime - English-translated">
        </a>
        </td>
        <td colspan="2">
        <a href="/view/2" title="Sample title 2">Sample title 2</a>
        </td>
        <td class="text-center" style="white-space: nowrap;">
        <a href="magnet:?xt=urn:btih:2"><i class="fa fa-fw fa-magnet"></i></a>
        </td>
        <td class="text-center">8.2 GiB</td>
        <td class="text-center" data-timestamp="1491608400" title="4 months 3
        weeks 4 days 19 hours 28 minutes 55 seconds ago">2017-04-08 01:40</td>
        <td class="text-center" style="color: green;">10</td>
        <td class="text-center" style="color: red;">1</td>
        <td class="text-center">206</td>
        </tr>
        </tbody>
        </table>
        """

        resp = mock.Mock(text=html)
        results = nyaa.response(resp)

        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)

        r = results[0]
        self.assertTrue(r['url'].find('1') >= 0)
        self.assertTrue(r['torrentfile'].find('1.torrent') >= 0)
        self.assertTrue(r['content'].find('Anime - English-translated') >= 0)
        self.assertTrue(r['content'].find('Downloaded 12 times.') >= 0)

        self.assertEqual(r['title'], 'Sample title 1')
        self.assertEqual(r['seed'], 1)
        self.assertEqual(r['leech'], 3)
        self.assertEqual(r['filesize'], 723700000)

        r = results[1]
        self.assertTrue(r['url'].find('2') >= 0)
        self.assertTrue(r['magnetlink'].find('magnet:') >= 0)
