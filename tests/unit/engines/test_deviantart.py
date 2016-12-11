from collections import defaultdict
import mock
from searx.engines import deviantart
from searx.testing import SearxTestCase


class TestDeviantartEngine(SearxTestCase):

    def test_request(self):
        dicto = defaultdict(dict)
        query = 'test_query'
        dicto['pageno'] = 0
        dicto['time_range'] = ''
        params = deviantart.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('deviantart.com' in params['url'])

    def test_no_url_in_request_year_time_range(self):
        dicto = defaultdict(dict)
        query = 'test_query'
        dicto['time_range'] = 'year'
        params = deviantart.request(query, dicto)
        self.assertEqual({}, params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, deviantart.response, None)
        self.assertRaises(AttributeError, deviantart.response, [])
        self.assertRaises(AttributeError, deviantart.response, '')
        self.assertRaises(AttributeError, deviantart.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(deviantart.response(response), [])

        response = mock.Mock(status_code=302)
        self.assertEqual(deviantart.response(response), [])

        html = """
        <div id="page-1-results" class="page-results results-page-thumb torpedo-container">
        <span class="thumb wide" href="http://amai911.deviantart.com/art/Horse-195212845"
        data-super-full-width="900" data-super-full-height="600">
            <a class="torpedo-thumb-link" href="https://url.of.image">
                <img data-sigil="torpedo-img" src="https://url.of.thumbnail" />
            </a>
        <span class="info"><span class="title-wrap"><span class="title">Title of image</span></span>
        </div>
        """
        response = mock.Mock(text=html)
        results = deviantart.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title of image')
        self.assertEqual(results[0]['url'], 'https://url.of.image')
        self.assertNotIn('content', results[0])
        self.assertEqual(results[0]['thumbnail_src'], 'https://url.of.thumbnail')

        html = """
        <span class="tt-fh-tc" style="width: 202px;">
            <span class="tt-bb" style="width: 202px;">
            </span>
            <span class="shadow">
                <a class="thumb" href="http://url.of.result/2nd.part.of.url"
                    title="Behoimi BE Animation Test by test-0, Jan 4,
                    2010 in Digital Art &gt; Animation"> <i></i>
                    <img width="200" height="200" alt="Test"
                        src="http://url.of.thumbnail" data-src="http://th08.deviantart.net/test.jpg">
                </a>
            </span>
            <!-- ^TTT -->
        </span>
        <span class="details">
            <a href="http://test-0.deviantart.com/art/Test" class="t"
                title="Behoimi BE Animation Test by test-0, Jan 4, 2010">
                <span class="tt-fh-oe">Title of image</span> </a>
            <small>
            <span class="category">
                <span class="age">
                    5 years ago
                </span>
                in <a title="Behoimi BE Animation Test by test-0, Jan 4, 2010"
                    href="http://www.deviantart.com/browse/all/digitalart/animation/">Animation</a>
            </span>
            <div class="commentcount">
                <a href="http://test-0.deviantart.com/art/Test#comments">
                <span class="iconcommentsstats"></span>9 Comments</a>
            </div>
            <a class="mlt-link" href="http://www.deviantart.com/morelikethis/149167425">
            <span class="mlt-icon"></span> <span class="mlt-text">More Like This</span> </a>
        </span>
        </small> <!-- TTT$ -->
        """
        response = mock.Mock(text=html)
        results = deviantart.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
