from collections import defaultdict
import mock
from searx.engines import digbt
from searx.testing import SearxTestCase


class TestDigBTEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = digbt.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('digbt.org', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, digbt.response, None)
        self.assertRaises(AttributeError, digbt.response, [])
        self.assertRaises(AttributeError, digbt.response, '')
        self.assertRaises(AttributeError, digbt.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(digbt.response(response), [])

        html = """
        <table class="table">
            <tr><td class="x-item">
            <div>
                <a title="The Big Bang Theory" class="title" href="/The-Big-Bang-Theory-d2.html">
                    The Big <span class="highlight">Bang</span> Theory
                </a>
                <span class="ctime"><span style="color:red;">4 hours ago</span></span>
            </div>
            <div class="files">
                <ul>
                    <li>The Big Bang Theory  2.9 GB</li>
                    <li>....</li>
                </ul>
            </div>
            <div class="tail">
                Files: 1 Size: 2.9 GB  Downloads: 1 Updated: <span style="color:red;">4 hours ago</span>
                &nbsp; &nbsp;
                <a class="title" href="magnet:?xt=urn:btih:a&amp;dn=The+Big+Bang+Theory">
                    <span class="glyphicon glyphicon-magnet"></span> magnet-link
                </a>
                &nbsp; &nbsp;
            </div>
            </td></tr>
        </table>
        """
        response = mock.Mock(text=html.encode('utf-8'))
        results = digbt.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'The Big Bang Theory')
        self.assertEqual(results[0]['url'], 'https://digbt.org/The-Big-Bang-Theory-d2.html')
        self.assertEqual(results[0]['content'], 'The Big Bang Theory 2.9 GB ....')
        self.assertEqual(results[0]['filesize'], 3113851289)
        self.assertEqual(results[0]['magnetlink'], 'magnet:?xt=urn:btih:a&dn=The+Big+Bang+Theory')
