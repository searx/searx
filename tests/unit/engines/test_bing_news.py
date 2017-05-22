from collections import defaultdict
import mock
from searx.engines import bing_news
from searx.testing import SearxTestCase
import lxml


class TestBingNewsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        dicto['time_range'] = ''
        params = bing_news.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('bing.com', params['url'])
        self.assertIn('fr', params['url'])

        dicto['language'] = 'all'
        params = bing_news.request(query, dicto)
        self.assertIn('en', params['url'])

    def test_no_url_in_request_year_time_range(self):
        dicto = defaultdict(dict)
        query = 'test_query'
        dicto['time_range'] = 'year'
        params = bing_news.request(query, dicto)
        self.assertEqual({}, params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, bing_news.response, None)
        self.assertRaises(AttributeError, bing_news.response, [])
        self.assertRaises(AttributeError, bing_news.response, '')
        self.assertRaises(AttributeError, bing_news.response, '[]')

        response = mock.Mock(content='<html></html>')
        self.assertEqual(bing_news.response(response), [])

        response = mock.Mock(content='<html></html>')
        self.assertEqual(bing_news.response(response), [])

        html = """<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0" xmlns:News="https://www.bing.com:443/news/search?q=python&amp;setmkt=en-US&amp;first=1&amp;format=RSS">
    <channel>
        <title>python - Bing News</title>
        <link>https://www.bing.com:443/news/search?q=python&amp;setmkt=en-US&amp;first=1&amp;format=RSS</link>
        <description>Search results</description>
        <image>
            <url>http://10.53.64.9/rsslogo.gif</url>
            <title>test</title>
            <link>https://www.bing.com:443/news/search?q=test&amp;setmkt=en-US&amp;first=1&amp;format=RSS</link>
        </image>
        <copyright>Copyright</copyright>
        <item>
            <title>Title</title>
            <link>https://www.bing.com/news/apiclick.aspx?ref=FexRss&amp;aid=&amp;tid=c237eccc50bd4758b106a5e3c94fce09&amp;url=http%3a%2f%2furl.of.article%2f&amp;c=xxxxxxxxx&amp;mkt=en-us</link>
            <description>Article Content</description>
            <pubDate>Tue, 02 Jun 2015 13:37:00 GMT</pubDate>
            <News:Source>Infoworld</News:Source>
            <News:Image>http://a1.bing4.com/th?id=ON.13371337133713371337133713371337&amp;pid=News</News:Image>
            <News:ImageSize>w={0}&amp;h={1}&amp;c=7</News:ImageSize>
            <News:ImageKeepOriginalRatio></News:ImageKeepOriginalRatio>
            <News:ImageMaxWidth>620</News:ImageMaxWidth>
            <News:ImageMaxHeight>413</News:ImageMaxHeight>
        </item>
        <item>
            <title>Another Title</title>
            <link>https://www.bing.com/news/apiclick.aspx?ref=FexRss&amp;aid=&amp;tid=c237eccc50bd4758b106a5e3c94fce09&amp;url=http%3a%2f%2fanother.url.of.article%2f&amp;c=xxxxxxxxx&amp;mkt=en-us</link>
            <description>Another Article Content</description>
            <pubDate>Tue, 02 Jun 2015 13:37:00 GMT</pubDate>
        </item>
    </channel>
</rss>"""  # noqa
        response = mock.Mock(content=html.encode('utf-8'))
        results = bing_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'http://url.of.article/')
        self.assertEqual(results[0]['content'], 'Article Content')
        self.assertEqual(results[0]['img_src'], 'https://www.bing.com/th?id=ON.13371337133713371337133713371337')
        self.assertEqual(results[1]['title'], 'Another Title')
        self.assertEqual(results[1]['url'], 'http://another.url.of.article/')
        self.assertEqual(results[1]['content'], 'Another Article Content')
        self.assertNotIn('img_src', results[1])

        html = """<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0" xmlns:News="https://www.bing.com:443/news/search?q=python&amp;setmkt=en-US&amp;first=1&amp;format=RSS">
    <channel>
        <title>python - Bing News</title>
        <link>https://www.bing.com:443/news/search?q=python&amp;setmkt=en-US&amp;first=1&amp;format=RSS</link>
        <description>Search results</description>
        <image>
            <url>http://10.53.64.9/rsslogo.gif</url>
            <title>test</title>
            <link>https://www.bing.com:443/news/search?q=test&amp;setmkt=en-US&amp;first=1&amp;format=RSS</link>
        </image>
        <copyright>Copyright</copyright>
        <item>
            <title>Title</title>
            <link>http://another.url.of.article/</link>
            <description>Article Content</description>
            <pubDate>garbage</pubDate>
            <News:Source>Infoworld</News:Source>
            <News:Image>http://another.bing.com/image</News:Image>
            <News:ImageSize>w={0}&amp;h={1}&amp;c=7</News:ImageSize>
            <News:ImageKeepOriginalRatio></News:ImageKeepOriginalRatio>
            <News:ImageMaxWidth>620</News:ImageMaxWidth>
            <News:ImageMaxHeight>413</News:ImageMaxHeight>
        </item>
    </channel>
</rss>"""  # noqa
        response = mock.Mock(content=html.encode('utf-8'))
        results = bing_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'http://another.url.of.article/')
        self.assertEqual(results[0]['content'], 'Article Content')
        self.assertEqual(results[0]['img_src'], 'http://another.bing.com/image')

        html = """<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0" xmlns:News="https://www.bing.com:443/news/search?q=python&amp;setmkt=en-US&amp;first=1&amp;format=RSS">
    <channel>
        <title>python - Bing News</title>
        <link>https://www.bing.com:443/news/search?q=python&amp;setmkt=en-US&amp;first=1&amp;format=RSS</link>
        <description>Search results</description>
        <image>
            <url>http://10.53.64.9/rsslogo.gif</url>
            <title>test</title>
            <link>https://www.bing.com:443/news/search?q=test&amp;setmkt=en-US&amp;first=1&amp;format=RSS</link>
        </image>
    </channel>
</rss>"""  # noqa

        response = mock.Mock(content=html.encode('utf-8'))
        results = bing_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        html = """<?xml version="1.0" encoding="utf-8" ?>gabarge"""
        response = mock.Mock(content=html.encode('utf-8'))
        self.assertRaises(lxml.etree.XMLSyntaxError, bing_news.response, response)
