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

    def test_sanitize_url(self):
        url = "test.url"
        self.assertEqual(url, yahoo_news.sanitize_url(url))

        url = "www.yahoo.com/;_ylt=test"
        self.assertEqual("www.yahoo.com/", yahoo_news.sanitize_url(url))

    def test_response(self):
        self.assertRaises(AttributeError, yahoo_news.response, None)
        self.assertRaises(AttributeError, yahoo_news.response, [])
        self.assertRaises(AttributeError, yahoo_news.response, '')
        self.assertRaises(AttributeError, yahoo_news.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(yahoo_news.response(response), [])

        html = """
        <ol class=" reg searchCenterMiddle">
            <li class="first">
                <div class="compTitle">
                    <h3>
                        <a class="yschttl spt" href="http://this.is.the.url" target="_blank">
                           This is
                           the <b>title</b>...
                        </a>
                    </h3>
                </div>
                <div>
                    <span class="cite">Business via Yahoo!</span>
                    <span class="tri fc-2nd ml-10">May 01 10:00 AM</span>
                </div>
                <div class="compText">
                   This is the content
               </div>
            </li>
            <li class="first">
                <div class="compTitle">
                    <h3>
                        <a class="yschttl spt" target="_blank">
                        </a>
                    </h3>
                </div>
                <div class="compText">
               </div>
            </li>
        </ol>
        """
        response = mock.Mock(text=html)
        results = yahoo_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title...')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url/')
        self.assertEqual(results[0]['content'], 'This is the content')

        html = """
        <ol class=" reg searchCenterMiddle">
            <li class="first">
                <div class="compTitle">
                    <h3>
                        <a class="yschttl spt" href="http://this.is.the.url" target="_blank">
                            This is
                            the <b>title</b>...
                        </a>
                    </h3>
                </div>
                <div>
                    <span class="cite">Business via Yahoo!</span>
                    <span class="tri fc-2nd ml-10">2 hours, 22 minutes ago</span>
                </div>
                <div class="compText">
                    This is the content
                </div>
            </li>
            <li>
                <div class="compTitle">
                    <h3>
                        <a class="yschttl spt" href="http://this.is.the.url" target="_blank">
                            This is
                            the <b>title</b>...
                        </a>
                    </h3>
                </div>
                <div>
                    <span class="cite">Business via Yahoo!</span>
                    <span class="tri fc-2nd ml-10">22 minutes ago</span>
                </div>
                <div class="compText">
                    This is the content
                </div>
            </li>
            <li>
                <div class="compTitle">
                    <h3>
                        <a class="yschttl spt" href="http://this.is.the.url" target="_blank">
                            This is
                            the <b>title</b>...
                        </a>
                    </h3>
                </div>
                <div>
                    <span class="cite">Business via Yahoo!</span>
                    <span class="tri fc-2nd ml-10">Feb 03 09:45AM 1900</span>
                </div>
                <div class="compText">
                    This is the content
                </div>
            </li>
        </ol>
        """
        response = mock.Mock(text=html)
        results = yahoo_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'This is the title...')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url/')
        self.assertEqual(results[0]['content'], 'This is the content')
        self.assertEqual(results[2]['publishedDate'].year, datetime.now().year)
