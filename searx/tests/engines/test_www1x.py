from collections import defaultdict
import mock
from searx.engines import www1x
from searx.testing import SearxTestCase


class TestWww1xEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        params = www1x.request(query, defaultdict(dict))
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('1x.com' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, www1x.response, None)
        self.assertRaises(AttributeError, www1x.response, [])
        self.assertRaises(AttributeError, www1x.response, '')
        self.assertRaises(AttributeError, www1x.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(www1x.response(response), [])
        html = """
        <?xml version="1.0" encoding="UTF-8"?><!DOCTYPE characters
        [
        <!ELEMENT characters (character*) >
        <!ELEMENT character  (#PCDATA   ) >

        <!ENTITY iexcl   "&#161;" >
        <!ENTITY cent    "&#162;" >
        <!ENTITY pound   "&#163;" >
        ]
        ><root><searchresult><![CDATA[<table border="0" cellpadding="0" cellspacing="0" width="100%">
        <tr>
            <td style="min-width: 220px;" valign="top">
                <div style="font-size: 30px; margin: 0px 0px 20px 0px;">Photos</div>
                <div>
                    <a href="/photo/123456" class="dynamiclink">
<img border="0" class="searchresult" src="/images/user/testimage-123456.jpg" style="width: 125px; height: 120px;">
                    </a>
                    <a title="sjoerd lammers street photography" href="/member/sjoerdlammers" class="dynamiclink">
<img border="0" class="searchresult" src="/images/profile/60c48b394c677d2fa4d9e7d263aabf44-square.jpg">
                    </a>
                </div>
            </td>
        </table>
        ]]></searchresult></root>
        """
        response = mock.Mock(text=html)
        results = www1x.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['url'], 'https://1x.com/photo/123456')
        self.assertEqual(results[0]['thumbnail_src'], 'https://1x.com/images/user/testimage-123456.jpg')
        self.assertEqual(results[0]['content'], '')
        self.assertEqual(results[0]['template'], 'images.html')
