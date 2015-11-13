# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import duckduckgo
from searx.testing import SearxTestCase


class TestDuckduckgoEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        params = duckduckgo.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('duckduckgo.com', params['url'])
        self.assertIn('fr-fr', params['url'])

        dicto['language'] = 'all'
        params = duckduckgo.request(query, dicto)
        self.assertIn('en-us', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, duckduckgo.response, None)
        self.assertRaises(AttributeError, duckduckgo.response, [])
        self.assertRaises(AttributeError, duckduckgo.response, '')
        self.assertRaises(AttributeError, duckduckgo.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(duckduckgo.response(response), [])

        html = u"""
        <div class="results_links results_links_deep web-result">
            <div class="icon_fav" style="display: block;">
                <a rel="nofollow" href="https://www.test.com/">
                    <img width="16" height="16" alt=""
                    src="/i/www.test.com.ico" style="visibility: visible;" name="i15" />
                </a>
            </div>
            <div class="links_main links_deep"> <!-- This is the visible part -->
                <a rel="nofollow" class="large" href="http://this.should.be.the.link/ű">
                    This <b>is</b> <b>the</b> title
                </a>
                <div class="snippet"><b>This</b> should be the content.</div>
                <div class="url">
                    http://this.should.be.the.link/
                </div>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = duckduckgo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], u'http://this.should.be.the.link/ű')
        self.assertEqual(results[0]['content'], 'This should be the content.')

        html = """
        <div class="results_links results_links_deep web-result">
            <div class="icon_fav" style="display: block;">
            </div>
            <div class="links_main links_deep"> <!-- This is the visible part -->
                <div class="snippet"><b>This</b> should be the content.</div>
                <div class="url">
                    http://this.should.be.the.link/
                </div>
            </div>
        </div>
        <div class="results_links results_links_deep web-result">
            <div class="icon_fav" style="display: block;">
                <img width="16" height="16" alt=""
                src="/i/www.test.com.ico" style="visibility: visible;" name="i15" />
            </div>
            <div class="links_main links_deep"> <!-- This is the visible part -->
                <a rel="nofollow" class="large" href="">
                    This <b>is</b> <b>the</b> title
                </a>
                <div class="snippet"><b>This</b> should be the content.</div>
                <div class="url">
                    http://this.should.be.the.link/
                </div>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = duckduckgo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
