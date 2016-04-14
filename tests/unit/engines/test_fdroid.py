import mock
from collections import defaultdict
from searx.engines import fdroid
from searx.testing import SearxTestCase


class TestFdroidEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dic = defaultdict(dict)
        dic['pageno'] = 1
        params = fdroid.request(query, dic)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('f-droid.org' in params['url'])

    def test_response(self):
        resp = mock.Mock(text='<html></html>')
        self.assertEqual(fdroid.response(resp), [])

        html = """
        <a href="https://google.com/qwerty">
          <div id="appheader">
            <div style="float:left;padding-right:10px;">
              <img src="http://example.com/image.png"
                   style="width:48px;border:none;">
            </div>
            <div style="float:right;">
              <p>Details...</p>
            </div>
            <p style="color:#000000;">
              <span style="font-size:20px;">Sample title</span>
              <br>
              Sample content
            </p>
          </div>
        </a>
        """

        resp = mock.Mock(text=html)
        results = fdroid.response(resp)

        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['url'], 'https://google.com/qwerty')
        self.assertEqual(results[0]['title'], 'Sample title')
        self.assertEqual(results[0]['content'], 'Sample content')
        self.assertEqual(results[0]['img_src'], 'http://example.com/image.png')
