from collections import defaultdict
import mock
from searx.engines import acgsou
from searx.testing import SearxTestCase


class TestAcgsouEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dic = defaultdict(dict)
        dic['pageno'] = 1
        params = acgsou.request(query, dic)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('acgsou.com' in params['url'])

    def test_response(self):
        resp = mock.Mock(text='<html></html>')
        self.assertEqual(acgsou.response(resp), [])

        html = """
        <html>
<table id="listTable" class="list_style table_fixed">
  <thead class="tcat">
      <tr>
        <th axis="string" class="l1 tableHeaderOver">test</th>
        <th axis="string" class="l2 tableHeaderOver">test</th>
        <th axis="string" class="l3 tableHeaderOver">test</th>
        <th axis="size" class="l4 tableHeaderOver">test</th>
        <th axis="number" class="l5 tableHeaderOver">test</th>
        <th axis="number" class="l6 tableHeaderOver">test</th>
        <th axis="number" class="l7 tableHeaderOver">test</th>
        <th axis="string" class="l8 tableHeaderOver">test</th>
      </tr>
  </thead>
  <tbody class="tbody" id="data_list">
 <tr class="alt1 ">
        <td nowrap="nowrap">date</td>
        <td><a href="category.html">testcategory</a></td>
        <td style="text-align:left;">
            <a href="show-torrentid.html" target="_blank">torrentname</a>
        </td>
        <td>1MB</td>
        <td nowrap="nowrap">
            <span class="bts_1">
            29
            </span>
        </td>
        <td nowrap="nowrap">
            <span class="btl_1">
            211
        </span>
        </td>
        <td nowrap="nowrap">
        <span class="btc_">
            168
        </span>
        </td>
        <td><a href="random.html">user</a></td>
      </tr>
      </tbody>
</table>
</html>
        """

        resp = mock.Mock(text=html)
        results = acgsou.response(resp)

        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)

        r = results[0]
        self.assertEqual(r['url'], 'https://www.acgsou.com/show-torrentid.html')
        self.assertEqual(r['content'], 'Category: "testcategory".')
        self.assertEqual(r['title'], 'torrentname')
        self.assertEqual(r['filesize'], 1048576)
