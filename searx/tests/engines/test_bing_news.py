from collections import defaultdict
import mock
from searx.engines import bing_news
from searx.testing import SearxTestCase


class TestBingNewsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        params = bing_news.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('bing.com', params['url'])
        self.assertIn('fr', params['url'])
        self.assertIn('_FP', params['cookies'])
        self.assertIn('en', params['cookies']['_FP'])

        dicto['language'] = 'all'
        params = bing_news.request(query, dicto)
        self.assertIn('en', params['url'])
        self.assertIn('_FP', params['cookies'])
        self.assertIn('en', params['cookies']['_FP'])

    def test_response(self):
        self.assertRaises(AttributeError, bing_news.response, None)
        self.assertRaises(AttributeError, bing_news.response, [])
        self.assertRaises(AttributeError, bing_news.response, '')
        self.assertRaises(AttributeError, bing_news.response, '[]')

        response = mock.Mock(content='<html></html>')
        self.assertEqual(bing_news.response(response), [])

        response = mock.Mock(content='<html></html>')
        self.assertEqual(bing_news.response(response), [])

        html = """
        <div class="sn_r">
            <div class="newstitle">
                <a href="http://url.of.article/" target="_blank" h="ID=news,5022.1">
                    Title
                </a>
            </div>
            <div class="sn_img">
                <a href="http://url.of.article2/" target="_blank" h="ID=news,5024.1">
                    <img class="rms_img" height="80" id="emb1" src="/image.src" title="Title" width="80" />
                </a>
            </div>
            <div class="sn_txt">
                <div class="sn_oi">
                    <span class="sn_snip">Article Content</span>
                    <div class="sn_ST">
                        <cite class="sn_src">metronews.fr</cite>
                        &nbsp;&#0183;&#32;
                        <span class="sn_tm">44 minutes ago</span>
                    </div>
                </div>
            </div>
        </div>
        """
        response = mock.Mock(content=html)
        results = bing_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'http://url.of.article/')
        self.assertEqual(results[0]['content'], 'Article Content')

        html = """
        <div class="sn_r">
            <div class="newstitle">
                <a href="http://url.of.article/" target="_blank" h="ID=news,5022.1">
                    Title
                </a>
            </div>
            <div class="sn_img">
                <a href="http://url.of.article2/" target="_blank" h="ID=news,5024.1">
                    <img class="rms_img" height="80" id="emb1" src="/image.src" title="Title" width="80" />
                </a>
            </div>
            <div class="sn_txt">
                <div class="sn_oi">
                    <span class="sn_snip">Article Content</span>
                    <div class="sn_ST">
                        <cite class="sn_src">metronews.fr</cite>
                        &nbsp;&#0183;&#32;
                        <span class="sn_tm">44 minutes ago</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="sn_r">
            <div class="newstitle">
                <a href="http://url.of.article/" target="_blank" h="ID=news,5022.1">
                    Title
                </a>
            </div>
            <div class="sn_img">
                <a href="http://url.of.article2/" target="_blank" h="ID=news,5024.1">
                    <img class="rms_img" height="80" id="emb1" src="/image.src" title="Title" width="80" />
                </a>
            </div>
            <div class="sn_txt">
                <div class="sn_oi">
                    <span class="sn_snip">Article Content</span>
                    <div class="sn_ST">
                        <cite class="sn_src">metronews.fr</cite>
                        &nbsp;&#0183;&#32;
                        <span class="sn_tm">3 hours, 44 minutes ago</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="sn_r">
            <div class="newstitle">
                <a href="http://url.of.article/" target="_blank" h="ID=news,5022.1">
                    Title
                </a>
            </div>
            <div class="sn_img">
                <a href="http://url.of.article2/" target="_blank" h="ID=news,5024.1">
                    <img class="rms_img" height="80" id="emb1" src="/image.src" title="Title" width="80" />
                </a>
            </div>
            <div class="sn_txt">
                <div class="sn_oi">
                    <span class="sn_snip">Article Content</span>
                    <div class="sn_ST">
                        <cite class="sn_src">metronews.fr</cite>
                        &nbsp;&#0183;&#32;
                        <span class="sn_tm">44 hours ago</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="sn_r">
            <div class="newstitle">
                <a href="http://url.of.article/" target="_blank" h="ID=news,5022.1">
                    Title
                </a>
            </div>
            <div class="sn_img">
                <a href="http://url.of.article2/" target="_blank" h="ID=news,5024.1">
                    <img class="rms_img" height="80" id="emb1" src="/image.src" title="Title" width="80" />
                </a>
            </div>
            <div class="sn_txt">
                <div class="sn_oi">
                    <span class="sn_snip">Article Content</span>
                    <div class="sn_ST">
                        <cite class="sn_src">metronews.fr</cite>
                        &nbsp;&#0183;&#32;
                        <span class="sn_tm">2 days ago</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="sn_r">
            <div class="newstitle">
                <a href="http://url.of.article/" target="_blank" h="ID=news,5022.1">
                    Title
                </a>
            </div>
            <div class="sn_img">
                <a href="http://url.of.article2/" target="_blank" h="ID=news,5024.1">
                    <img class="rms_img" height="80" id="emb1" src="/image.src" title="Title" width="80" />
                </a>
            </div>
            <div class="sn_txt">
                <div class="sn_oi">
                    <span class="sn_snip">Article Content</span>
                    <div class="sn_ST">
                        <cite class="sn_src">metronews.fr</cite>
                        &nbsp;&#0183;&#32;
                        <span class="sn_tm">27/01/2015</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="sn_r">
            <div class="newstitle">
                <a href="http://url.of.article/" target="_blank" h="ID=news,5022.1">
                    Title
                </a>
            </div>
            <div class="sn_img">
                <a href="http://url.of.article2/" target="_blank" h="ID=news,5024.1">
                    <img class="rms_img" height="80" id="emb1" src="/image.src" title="Title" width="80" />
                </a>
            </div>
            <div class="sn_txt">
                <div class="sn_oi">
                    <span class="sn_snip">Article Content</span>
                    <div class="sn_ST">
                        <cite class="sn_src">metronews.fr</cite>
                        &nbsp;&#0183;&#32;
                        <span class="sn_tm">Il y a 3 heures</span>
                    </div>
                </div>
            </div>
        </div>
        """
        response = mock.Mock(content=html)
        results = bing_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 6)

        html = """
        <div class="newstitle">
            <a href="http://url.of.article/" target="_blank" h="ID=news,5022.1">
                Title
            </a>
        </div>
        <div class="sn_img">
            <a href="http://url.of.article2/" target="_blank" h="ID=news,5024.1">
                <img class="rms_img" height="80" id="emb1" src="/image.src" title="Title" width="80" />
            </a>
        </div>
        <div class="sn_txt">
            <div class="sn_oi">
                <span class="sn_snip">Article Content</span>
                <div class="sn_ST">
                    <cite class="sn_src">metronews.fr</cite>
                    &nbsp;&#0183;&#32;
                    <span class="sn_tm">44 minutes ago</span>
                </div>
            </div>
        </div>
        """
        response = mock.Mock(content=html)
        results = bing_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
