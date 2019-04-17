from collections import defaultdict
import mock
from searx.engines import deviantart
from searx.testing import SearxTestCase
import lxml


class TestDeviantartEngine(SearxTestCase):

    def test_request(self):
        dicto = defaultdict(dict)
        query = 'test_query'
        dicto['pageno'] = 0
        dicto['time_range'] = ''
        params = deviantart.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('deviantart.com' in params['url'])

    def test_no_url_in_request_year_time_range(self):
        dicto = defaultdict(dict)
        query = 'test_query'
        dicto['time_range'] = 'year'
        params = deviantart.request(query, dicto)
        self.assertEqual({}, params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, deviantart.response, None)
        self.assertRaises(AttributeError, deviantart.response, [])
        self.assertRaises(AttributeError, deviantart.response, '')
        self.assertRaises(AttributeError, deviantart.response, '[]')

        response = mock.Mock(content='<html></html>')
        self.assertEqual(deviantart.response(response), [])

        # correctness test
        rss = """
<rss xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:creativeCommons="http://backend.userland.com/creativeCommonsRssModule" version="2.0">
  <channel>
    <title>DeviantArt: Popular Test</title>
    <link>https://www.deviantart.com/popular-all-time/?q=test</link>
    <description>DeviantArt RSS for Popular Test</description>
    <language>en-us</language>
    <copyright>Copyright 2019, DeviantArt.com</copyright>
    <pubDate>Wed, 17 Apr 2019 15:39:48 PDT</pubDate>
    <generator>DeviantArt.com</generator>
    <docs>http://blogs.law.harvard.edu/tech/rss</docs>
    <atom:icon>https://st.deviantart.net/minish/touch-icons/android-192.png</atom:icon>
    <atom:link type="application/rss+xml" rel="self" href="https://backend.deviantart.com/rss.xml?type=deviation&amp;q=test&amp;order=9"/>
    <atom:link rel="next" href="https://backend.deviantart.com/rss.xml?type=deviation&amp;q=test&amp;order=9&amp;offset=60"/>
    <item>
      <title>Test 1 title</title>
      <link>https://www.deviantart.com/testauthor/art/Test-1</link>
      <guid isPermaLink="true">https://www.deviantart.com/testauthor/art/Test-1</guid>
      <pubDate>Fri, 08 Jun 2012 12:47:04 PDT</pubDate>
      <media:title type="plain">Test</media:title>
      <media:keywords/>
      <media:rating>nonadult</media:rating>
      <media:credit role="author" scheme="urn:ebu">TestAuthor</media:credit>
      <media:credit role="author" scheme="urn:ebu">https://a.deviantart.net/avatars/t/e/testauthor.jpg?7</media:credit>
      <media:copyright url="https://www.deviantart.com/testauthor">Copyright TestAuthor</media:copyright>
      <media:description type="html">testdescription</media:description>
      <media:thumbnail url="https://t00.deviantart.net/testthumb_small_1.jpg" height="89" width="150"/>
      <media:thumbnail url="https://t00.deviantart.net/testthumb_large_1.jpg" height="178" width="300"/>
      <media:thumbnail url="https://t00.deviantart.net/testthumb_square_1.jpg" height="178" width="178"/>
      <media:content url="https://orig00.deviantart.net/test_1.jpg" height="476" width="802" medium="image"/>
      <description>testdescription</description>
    </item>
  </channel>
</rss>
        """
        response = mock.Mock(content=rss)
        results = deviantart.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test 1 title')
        self.assertEqual(results[0]['content'], 'testdescription')
        self.assertEqual(results[0]['author'], 'TestAuthor')
        self.assertEqual(results[0]['source'], 'Copyright TestAuthor')
        self.assertEqual(results[0]['img_format'], 'jpg 802x476')
        self.assertEqual(results[0]['img_src'], 'https://orig00.deviantart.net/test_1.jpg')
        self.assertEqual(results[0]['thumbnail_src'], 'https://t00.deviantart.net/testthumb_large_1.jpg')
        self.assertEqual(results[0]['url'], 'https://www.deviantart.com/testauthor/art/Test-1')

        # garbage test
        html = """
<HTML><HEAD><TITLE>ERROR: Fluxcapacitor discharged, need 1.21 gigawatts to charge</TITLE></HEAD><BODY>
<H1>403 ERROR</H1>
<PRE>
This is only a test
</PRE>
</BODY></HTML>
        """
        response = mock.Mock(content=html)
        results = deviantart.response(response)
        self.assertEqual(deviantart.response(response), [])

