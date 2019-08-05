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
        self.assertTrue('search.f-droid.org' in params['url'])

    def test_response_empty(self):
        resp = mock.Mock(text='<html></html>')
        self.assertEqual(fdroid.response(resp), [])

    def test_response_oneresult(self):
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>test</title>
</head>
<body>
    <div class="site-wrapper">
        <div class="main-content">
            <a class="package-header" href="https://example.com/app.url">
                <img class="package-icon" src="https://example.com/appexample.logo.png" />

                <div class="package-info">
                    <h4 class="package-name">
                        App Example 1
                    </h4>

                    <div class="package-desc">
                        <span class="package-summary">Description App Example 1</span>
                        <span class="package-license">GPL-3.0-only</span>
                    </div>
                </div>
            </a>
        </div>
    </div>
</body>
</html>
        """

        resp = mock.Mock(text=html)
        results = fdroid.response(resp)

        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['url'], 'https://example.com/app.url')
        self.assertEqual(results[0]['title'], 'App Example 1')
        self.assertEqual(results[0]['content'], 'Description App Example 1 - GPL-3.0-only')
        self.assertEqual(results[0]['img_src'], 'https://example.com/appexample.logo.png')
