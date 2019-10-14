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

        dicto['language'] = 'all'
        params = startpage.request(query, dicto)

    def test_response(self):
        self.assertRaises(AttributeError, startpage.response, None)
        self.assertRaises(AttributeError, startpage.response, [])
        self.assertRaises(AttributeError, startpage.response, '')
        self.assertRaises(AttributeError, startpage.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(startpage.response(response), [])

        html = """
<div class="w-gl__result">
                <a
                    class="w-gl__result-title"
                    href="http://this.should.be.the.link/"
                    data-onw="1"
                    rel="noopener noreferrer"
                    target="_blank">

                    <h3>This should be the title</h3>
                </a>
                <div class="w-gl__result-second-line-container">
                    <div class="w-gl__result-url-container">
                        <a
                            class="w-gl__result-url"
                            href="http://this.should.be.the.link/"
                            rel="noopener noreferrer"
                            target="_blank">https://www.cnbc.com/2019/10/12/dj-zedd-banned-in-china-for-liking-a-south-park-tweet.html</a>
                    </div>
                    <a
                        class="w-gl__anonymous-view-url"
                        href="https://eu-browse.startpage.com/do/proxy?ep=556b554d576b6f5054554546423167764b5445616455554d5342675441774659495246304848774f5267385453304941486b5949546c63704e33774f526b705544565647516d4a61554246304847674f4a556f6957415a4f436b455042426b6b4f7a64535a52784a56514a4f45307743446c567250445a4f4c52514e5677554e46776b4b545563704c7931554c5167465467644f42464d4f4255426f4d693152624634525741305845526c595746636b626d67494e42705743466c515252634f4267456e597a7346596b7856435134465345634f564249794b5752785643315863546769515773764a5163494c5877505246315865456f5141426b4f41774167596d6c5a4e30395758773442465251495677596c624770665a6b786344466b4151455663425249794d6a78525a55554157516f4342556766526b51314b57514e&amp;ek=4q58686o5047786n6343527259445247576p6o38&amp;ekdata=84abd523dc13cba5c65164d04d7d7263"
                        target="_blank">Anonymous View</a>
                </div>
                <p class="w-gl__description">This should be the content.</p>
            </div>
        """  # noqa
        response = mock.Mock(text=html.encode('utf-8'))
        results = startpage.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This should be the title')
        self.assertEqual(results[0]['url'], 'http://this.should.be.the.link/')
        self.assertEqual(results[0]['content'], 'This should be the content.')
