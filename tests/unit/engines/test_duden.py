from collections import defaultdict
import mock
from searx.engines import duden
from searx.testing import SearxTestCase
from datetime import datetime


class TestDudenEngine(SearxTestCase):

    def test_request(self):
        query = 'Haus'
        dic = defaultdict(dict)
        dic['pageno'] = 1
        params = duden.request(query, dic)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('duden.de' in params['url'])

    def test_response(self):
        resp = mock.Mock(text='<html></html>')
        self.assertEqual(duden.response(resp), [])

        html = """
        <section class="wide">
        <h2><a href="https://this.is.the.url/" class="hidden-link"><strong>This is the title</strong> also here</a></h2>
        <p>This is the <strong>content</strong></p>
        <a href="https://this.is.the.url/">Zum vollst&auml;ndigen Artikel</a>
        </section>
        """

        resp = mock.Mock(text=html)
        results = duden.response(resp)

        self.assertEqual(len(results), 1)
        self.assertEqual(type(results), list)

        # testing result (dictionary entry)
        r = results[0]
        self.assertEqual(r['url'], 'https://this.is.the.url/')
        self.assertEqual(r['title'], 'This is the title also here')
        self.assertEqual(r['content'], 'This is the content')
