from collections import defaultdict
import mock
from searx.engines import duden
from searx.testing import SearxTestCase
from datetime import datetime


class TestDudenEngine(SearxTestCase):

    def test_request(self):
        query = 'Haus'
        dic = defaultdict(dict)
        data = [
            [1, 'https://www.duden.de/suchen/dudenonline/Haus'],
            [2, 'https://www.duden.de/suchen/dudenonline/Haus?search_api_fulltext=&page=1']
        ]
        for page_no, exp_res in data:
            dic['pageno'] = page_no
            params = duden.request(query, dic)
            self.assertTrue('url' in params)
            self.assertTrue(query in params['url'])
            self.assertTrue('duden.de' in params['url'])
            self.assertEqual(params['url'], exp_res)

    def test_response(self):
        resp = mock.Mock(text='<html></html>')
        self.assertEqual(duden.response(resp), [])

        html = """
        <section class="vignette">
            <h2"> <a href="/rechtschreibung/Haus">
                <strong>This is the title also here</strong>
            </a> </h2>
          <p>This is the content</p>
        </section>
        """
        resp = mock.Mock(text=html)
        results = duden.response(resp)

        self.assertEqual(len(results), 1)
        self.assertEqual(type(results), list)

        # testing result (dictionary entry)
        r = results[0]
        self.assertEqual(r['url'], 'https://www.duden.de/rechtschreibung/Haus')
        self.assertEqual(r['title'], 'This is the title also here')
        self.assertEqual(r['content'], 'This is the content')
