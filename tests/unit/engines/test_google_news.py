# -*- coding: utf-8 -*-

from collections import defaultdict
import mock
from searx.engines import google_news
from searx.testing import SearxTestCase


class TestGoogleNewsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        dicto['time_range'] = 'w'
        params = google_news.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('fr', params['url'])

        dicto['language'] = 'all'
        params = google_news.request(query, dicto)
        self.assertIn('url', params)
        self.assertNotIn('fr', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, google_news.response, None)
        self.assertRaises(AttributeError, google_news.response, [])
        self.assertRaises(AttributeError, google_news.response, '')
        self.assertRaises(AttributeError, google_news.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(google_news.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(google_news.response(response), [])

        html = u"""
<h2 class="hd">Search Results</h2>
<div data-async-context="query:searx" id="ires">
    <div eid="oC2oWcGXCafR6ASkwoCwDA" id="rso">
        <div class="_NId">
            <!--m-->
            <div class="g _cy">
                <div class="ts _JGs _JHs _tJs _KGs _jHs">
                    <div class="_hJs">
                        <h3 class="r _gJs">
                            <a class="l _PMs" href="https://example.com/" onmousedown="return rwt(this,'','','','11','AFQjCNEyehpzD5cJK1KUfXBx9RmsbqqG9g','','0ahUKEwjB58OR54HWAhWnKJoKHSQhAMY4ChCpAggiKAAwAA','','',event)">Example title</a>
                        </h3>
                        <div class="slp">
                            <span class="_OHs _PHs">
                                Mac &amp; i</span>
                            <span class="_QGs">
                                -</span>
                            <span class="f nsa _QHs">
                                Mar 21, 2016</span>
                        </div>
                        <div class="st">Example description</div>
                    </div>
                </div>
            </div>
            <div class="g _cy">
                <div class="ts _JGs _JHs _oGs _KGs _jHs">
                    <a class="top _xGs _SHs" href="https://example2.com/" onmousedown="return rwt(this,'','','','12','AFQjCNHObfH7sYmLWI1SC-YhWXKZFRzRjw','','0ahUKEwjB58OR54HWAhWnKJoKHSQhAMY4ChC8iAEIJDAB','','',event)">
                        <img class="th _RGs" src="https://example2.com/image.jpg" alt="Story image for searx from Golem.de" onload="typeof google==='object'&&google.aft&&google.aft(this)">
                    </a>
                    <div class="_hJs">
                        <h3 class="r _gJs">
                            <a class="l _PMs" href="https://example2.com/" onmousedown="return rwt(this,'','','','12','AFQjCNHObfH7sYmLWI1SC-YhWXKZFRzRjw','','0ahUKEwjB58OR54HWAhWnKJoKHSQhAMY4ChCpAgglKAAwAQ','','',event)">Example title 2</a>
                        </h3>
                        <div class="slp">
                            <span class="_OHs _PHs">
                                Golem.de</span>
                            <span class="_QGs">
                                -</span>
                            <span class="f nsa _QHs">
                                Oct 4, 2016</span>
                        </div>
                        <div class="st">Example description 2</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>


        """  # noqa
        response = mock.Mock(text=html)
        results = google_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], u'Example title')
        self.assertEqual(results[0]['url'], 'https://example.com/')
        self.assertEqual(results[0]['content'], 'Example description')
        self.assertEqual(results[1]['title'], u'Example title 2')
        self.assertEqual(results[1]['url'], 'https://example2.com/')
        self.assertEqual(results[1]['content'], 'Example description 2')
        self.assertEqual(results[1]['img_src'], 'https://example2.com/image.jpg')
