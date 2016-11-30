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
        <div class='result' style=' *width : auto; *margin-right : 10%;'>
            <h3>
                <a href='http://this.should.be.the.link/' id='title_2' name='title_2' >
                    This should be the title
                </a>
                <span id='title_stars_2' name='title_stars_2'>  </span>
            </h3>
            <p class='desc clk'>
                This should be the content.
            </p>
            <p>
                <span class='url'>www.speed<b>test</b>.net/fr/
                </span>
                  -
                <A class="proxy" id="proxy_link" HREF="https://ixquick-proxy.com/do/spg/proxy?ep=&edata=&ek=&ekdata="
                    class='proxy'>
                    Navigation avec Ixquick Proxy
                </A>
                    -
                <A HREF="https://ixquick-proxy.com/do/spg/highlight.pl?l=francais&c=hf&cat=web&q=test&rl=NONE&rid=
                    &hlq=https://startpage.com/do/search&mtabp=-1&mtcmd=process_search&mtlanguage=francais&mtengine0=
                    &mtcat=web&u=http:%2F%2Fwww.speedtest.net%2Ffr%2F" class='proxy'>
                    Mis en surbrillance
                </A>
            </p>
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
        <div class='result' style=' *width : auto; *margin-right : 10%;'>
            <h3>
                <a href='http://www.google.com/aclk?sa=l&ai=C' id='title_2' name='title_2' >
                    This should be the title
                </a>
                <span id='title_stars_2' name='title_stars_2'>  </span>
            </h3>
            <p class='desc clk'>
                This should be the content.
            </p>
            <p>
                <span class='url'>www.speed<b>test</b>.net/fr/
                </span>
                  -
                <A class="proxy" id="proxy_link" HREF="https://ixquick-proxy.com/do/spg/proxy?ep=&edata=&ek=&ekdata="
                    class='proxy'>
                    Navigation avec Ixquick Proxy
                </A>
                    -
                <A HREF="https://ixquick-proxy.com/do/spg/highlight.pl?l=francais&c=hf&cat=web&q=test&rl=NONE&rid=
                    &hlq=https://startpage.com/do/search&mtabp=-1&mtcmd=process_search&mtlanguage=francais&mtengine0=
                    &mtcat=web&u=http:%2F%2Fwww.speedtest.net%2Ffr%2F" class='proxy'>
                    Mis en surbrillance
                </A>
            </p>
        </div>
        <div class='result' style=' *width : auto; *margin-right : 10%;'>
            <h3>
                <span id='title_stars_2' name='title_stars_2'>  </span>
            </h3>
            <p class='desc clk'>
                This should be the content.
            </p>
            <p>
                <span class='url'>www.speed<b>test</b>.net/fr/
                </span>
            </p>
        </div>
        <div class='result' style=' *width : auto; *margin-right : 10%;'>
            <h3>
                <a href='http://this.should.be.the.link/' id='title_2' name='title_2' >
                    This should be the title
                </a>
                <span id='title_stars_2' name='title_stars_2'>  </span>
            </h3>
            <p>
                <span class='url'>www.speed<b>test</b>.net/fr/
                </span>
                  -
                <A class="proxy" id="proxy_link" HREF="https://ixquick-proxy.com/do/spg/proxy?ep=&edata=&ek=&ekdata="
                    class='proxy'>
                    Navigation avec Ixquick Proxy
                </A>
                    -
                <A HREF="https://ixquick-proxy.com/do/spg/highlight.pl?l=francais&c=hf&cat=web&q=test&rl=NONE&rid=
                    &hlq=https://startpage.com/do/search&mtabp=-1&mtcmd=process_search&mtlanguage=francais&mtengine0=
                    &mtcat=web&u=http:%2F%2Fwww.speedtest.net%2Ffr%2F" class='proxy'>
                    Mis en surbrillance
                </A>
            </p>
        </div>
        """
        response = mock.Mock(text=html.encode('utf-8'))
        results = startpage.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], '')
