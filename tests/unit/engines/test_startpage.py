# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import startpage
from searx.testing import SearxTestCase


class TestStartpageEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        params = startpage.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn('startpage.com', params['url'])
        self.assertIn('data', params)
        self.assertIn('query', params['data'])
        self.assertIn(query, params['data']['query'])
        self.assertIn('with_language', params['data'])
        self.assertIn('lang_fr', params['data']['with_language'])

        dicto['language'] = 'all'
        params = startpage.request(query, dicto)
        self.assertNotIn('with_language', params['data'])

    def test_response(self):
        self.assertRaises(AttributeError, startpage.response, None)
        self.assertRaises(AttributeError, startpage.response, [])
        self.assertRaises(AttributeError, startpage.response, '')
        self.assertRaises(AttributeError, startpage.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(startpage.response(response), [])

        html = """
        <div class="w-gl__result">
            <a class="w-gl__result-title"
            href="http://this.should.be.the.link/"
            data-onw="1"
            rel="noopener noreferrer"
            target="_blank">
                <h3>This should be the title</h3>
            </a>
            <a class="w-gl__result-url"
            href="http://this.should.be.the.link/"
            rel="noopener noreferrer"
            target="_blank">
                http://this.should.be.the.link/
            </a>
            <a class="w-gl__anonymous-view-url"
            href="https://eu-browse.startpage.com/do/proxy?ep=&edata=&ek=&ekdata="
            target="_blank">
                Anonymous View
            </a>
            <br>
            <span>
                This should be the content.
            </span>
        </div>
        """
        response = mock.Mock(text=html.encode('utf-8'))
        results = startpage.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This should be the title')
        self.assertEqual(results[0]['url'], 'http://this.should.be.the.link/')
        self.assertEqual(results[0]['content'], 'This should be the content.')

        html = """
        <div class="w-gl__result">
            <a class="w-gl__result-title"
            href="http://www.google.com/aclk?sa=l&ai=C"
            data-onw="1"
            rel="noopener noreferrer"
            target="_blank">
                <h3>This should be the title</h3>
            </a>
            <a class="w-gl__result-url"
            href="www.speedtest.net/fr/"
            rel="noopener noreferrer"
            target="_blank">
                www.speedtest.net/fr/
            </a>
            <a class="w-gl__anonymous-view-url"
            href="https://eu-browse.startpage.com/do/proxy?ep=&edata=&ek=&ekdata="
            target="_blank">
                Anonymous View
            </a>
            <br>
            <span>
                This should be the content.
            </span>
        </div>
        <div class="w-gl__result">
            <a class="w-gl__result-url"
            href="www.speedtest.net/fr/"
            rel="noopener noreferrer"
            target="_blank">
                www.speedtest.net/fr/
            </a>
            <a class="w-gl__anonymous-view-url"
            href="https://eu-browse.startpage.com/do/proxy?ep=&edata=&ek=&ekdata="
            target="_blank">
                Anonymous View
            </a>
            <br>
            <span>
                This should be the content.
            </span>
        </div>
        <div class="w-gl__result">
            <a class="w-gl__result-title" href="http://this.should.be.the.link/"
            data-onw="1"
            rel="noopener noreferrer"
            target="_blank">
                <h3>This should be the title</h3>
            </a>
            <a class="w-gl__result-url"
            href="www.speedtest.net/fr/"
            rel="noopener noreferrer"
            target="_blank">
                www.speedtest.net/fr/
            </a>
            <a class="w-gl__anonymous-view-url"
            href="https://eu-browse.startpage.com/do/proxy?ep=&edata=&ek=&ekdata="
            target="_blank">
                Anonymous View
            </a>
            <br>
        </div>
        """
        response = mock.Mock(text=html.encode('utf-8'))
        results = startpage.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], '')
