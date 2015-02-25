# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime
import mock
from searx.engines import yahoo_news
from searx.testing import SearxTestCase


class TestYahooNewsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        params = yahoo_news.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('news.search.yahoo.com', params['url'])
        self.assertIn('fr', params['url'])
        self.assertIn('cookies', params)
        self.assertIn('sB', params['cookies'])
        self.assertIn('fr', params['cookies']['sB'])

        dicto['language'] = 'all'
        params = yahoo_news.request(query, dicto)
        self.assertIn('cookies', params)
        self.assertIn('sB', params['cookies'])
        self.assertIn('en', params['cookies']['sB'])
        self.assertIn('en', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, yahoo_news.response, None)
        self.assertRaises(AttributeError, yahoo_news.response, [])
        self.assertRaises(AttributeError, yahoo_news.response, '')
        self.assertRaises(AttributeError, yahoo_news.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(yahoo_news.response(response), [])

        html = """
        <div class="res">
            <div>
                <h3>
                    <a class="yschttl spt" href="http://this.is.the.url" target="_blank">
                        This is
                        the <b>title</b>...
                    </a>
                </h3>
            </div>
            <span class="url">Business via Yahoo! Finance</span> &nbsp; <span class="timestamp">Feb 03 09:45am</span>
            <div class="abstr">
                This is the content
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = yahoo_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title...')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url/')
        self.assertEqual(results[0]['content'], 'This is the content')

        html = """
        <div class="res">
            <div>
                <h3>
                    <a class="yschttl spt" href="http://this.is.the.url" target="_blank">
                        This is
                        the <b>title</b>...
                    </a>
                </h3>
            </div>
            <span class="url">Business via Yahoo!</span> &nbsp; <span class="timestamp">2 hours, 22 minutes ago</span>
            <div class="abstr">
                This is the content
            </div>
        </div>
        <div class="res">
            <div>
                <h3>
                    <a class="yschttl spt" href="http://this.is.the.url" target="_blank">
                        This is
                        the <b>title</b>...
                    </a>
                </h3>
            </div>
            <span class="url">Business via Yahoo!</span> &nbsp; <span class="timestamp">22 minutes ago</span>
            <div class="abstr">
                This is the content
            </div>
        </div>
        <div class="res">
            <div>
                <h3>
                    <a class="yschttl spt" href="http://this.is.the.url" target="_blank">
                        This is
                        the <b>title</b>...
                    </a>
                </h3>
            </div>
            <span class="url">Business via Yahoo!</span> &nbsp; <span class="timestamp">Feb 03 09:45am 1900</span>
            <div class="abstr">
                This is the content
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = yahoo_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'This is the title...')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url/')
        self.assertEqual(results[0]['content'], 'This is the content')
        self.assertEqual(results[2]['publishedDate'].year, datetime.now().year)

        html = """
        <li class="b_algo" u="0|5109|4755453613245655|UAGjXgIrPH5yh-o5oNHRx_3Zta87f_QO">
            <div Class="sa_mc">
                <div class="sb_tlst">
                    <h2>
                        <a href="http://this.should.be.the.link/" h="ID=SERP,5124.1">
                        <strong>This</strong> should be the title</a>
                    </h2>
                </div>
                <div class="sb_meta">
                <cite>
                <strong>this</strong>.meta.com</cite>
                    <span class="c_tlbxTrg">
                        <span class="c_tlbxH" H="BASE:CACHEDPAGEDEFAULT" K="SERP,5125.1">
                        </span>
                    </span>
                </div>
                <p>
                <strong>This</strong> should be the content.</p>
            </div>
        </li>
        """
        response = mock.Mock(text=html)
        results = yahoo_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
