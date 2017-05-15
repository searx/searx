from collections import defaultdict
import mock
from searx.engines import bing
from searx.testing import SearxTestCase


class TestBingEngine(SearxTestCase):

    def test_request(self):
        query = u'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['language'] = 'fr_FR'
        params = bing.request(query.encode('utf-8'), dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('language%3AFR' in params['url'])
        self.assertTrue('bing.com' in params['url'])

        dicto['language'] = 'all'
        params = bing.request(query.encode('utf-8'), dicto)
        self.assertTrue('language' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, bing.response, None)
        self.assertRaises(AttributeError, bing.response, [])
        self.assertRaises(AttributeError, bing.response, '')
        self.assertRaises(AttributeError, bing.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(bing.response(response), [])

        response = mock.Mock(text='<html></html>')
        self.assertEqual(bing.response(response), [])

        html = """
        <div class="sa_cc" u="0|5109|4755453613245655|UAGjXgIrPH5yh-o5oNHRx_3Zta87f_QO">
            <div Class="sa_mc">
                <div class="sb_tlst">
                    <h3>
                        <a href="http://this.should.be.the.link/" h="ID=SERP,5124.1">
                        <strong>This</strong> should be the title</a>
                    </h3>
                </div>
                <div class="sb_meta"><cite><strong>this</strong>.meta.com</cite>
                    <span class="c_tlbxTrg">
                        <span class="c_tlbxH" H="BASE:CACHEDPAGEDEFAULT" K="SERP,5125.1">
                        </span>
                    </span>
                </div>
                <p><strong>This</strong> should be the content.</p>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = bing.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This should be the title')
        self.assertEqual(results[0]['url'], 'http://this.should.be.the.link/')
        self.assertEqual(results[0]['content'], 'This should be the content.')

        html = """
        <li class="b_algo" u="0|5109|4755453613245655|UAGjXgIrPH5yh-o5oNHRx_3Zta87f_QO">
            <div Class="sa_mc">
                <div class="sb_tlst">
                    <h2>
                        <a href="http://this.should.be.the.link/" h="ID=SERP,5124.1">
                        <strong>This</strong> should be the title</a>
                    </h2>
                </div>
                <div class="sb_meta"><cite><strong>this</strong>.meta.com</cite>
                    <span class="c_tlbxTrg">
                        <span class="c_tlbxH" H="BASE:CACHEDPAGEDEFAULT" K="SERP,5125.1">
                        </span>
                    </span>
                </div>
                <p><strong>This</strong> should be the content.</p>
            </div>
        </li>
        """
        response = mock.Mock(text=html)
        results = bing.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This should be the title')
        self.assertEqual(results[0]['url'], 'http://this.should.be.the.link/')
        self.assertEqual(results[0]['content'], 'This should be the content.')

    def test_fetch_supported_languages(self):
        html = """<html></html>"""
        response = mock.Mock(text=html)
        results = bing._fetch_supported_languages(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        html = """
        <html>
            <body>
                <form>
                    <div id="limit-languages">
                        <div>
                            <div><input id="es" value="es"></input></div>
                        </div>
                        <div>
                            <div><input id="pt_BR" value="pt_BR"></input></div>
                            <div><input id="pt_PT" value="pt_PT"></input></div>
                        </div>
                    </div>
                </form>
            </body>
        </html>
        """
        response = mock.Mock(text=html)
        languages = bing._fetch_supported_languages(response)
        self.assertEqual(type(languages), list)
        self.assertEqual(len(languages), 3)
        self.assertIn('es', languages)
        self.assertIn('pt-BR', languages)
        self.assertIn('pt-PT', languages)
