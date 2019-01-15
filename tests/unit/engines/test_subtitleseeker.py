from collections import defaultdict
import mock
from searx.engines import subtitleseeker
from searx.testing import SearxTestCase


class TestSubtitleseekerEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr-FR'
        params = subtitleseeker.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('subtitleseeker.com' in params['url'])

    def test_response(self):
        dicto = defaultdict(dict)
        dicto['language'] = 'fr-FR'
        response = mock.Mock(search_params=dicto)

        self.assertRaises(AttributeError, subtitleseeker.response, None)
        self.assertRaises(AttributeError, subtitleseeker.response, [])
        self.assertRaises(AttributeError, subtitleseeker.response, '')
        self.assertRaises(AttributeError, subtitleseeker.response, '[]')

        response = mock.Mock(text='<html></html>', search_params=dicto)
        self.assertEqual(subtitleseeker.response(response), [])

        html = """
        <div class="boxRows">
            <div class="boxRowsInner" style="width:600px;">
                <img src="http://static.subtitleseeker.com/images/movie.gif"
                    style="width:16px; height:16px;" class="icon">
                <a href="http://this.is.the.url/"
                    class="blue" title="Title subtitle" >
                    This is the Title
                </a>
                <br><br>
                <span class="f10b grey-dark arial" style="padding:0px 0px 5px 20px">
                    "Alternative Title"
                </span>
            </div>
            <div class="boxRowsInner f12b red" style="width:70px;">
                1998
            </div>
            <div class="boxRowsInner grey-web f12" style="width:120px;">
                <img src="http://static.subtitleseeker.com/images/basket_put.png"
                    style="width:16px; height:16px;" class="icon">
                1039 Subs
            </div>
            <div class="boxRowsInner grey-web f10" style="width:130px;">
                <img src="http://static.subtitleseeker.com/images/arrow_refresh_small.png"
                    style="width:16px; height:16px;" class="icon">
                1 hours ago
            </div>
            <div class="clear"></div>
        </div>
        """
        response = mock.Mock(text=html, search_params=dicto)
        results = subtitleseeker.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the Title')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url/French/')
        self.assertIn('1998', results[0]['content'])
        self.assertIn('1039 Subs', results[0]['content'])
        self.assertIn('Alternative Title', results[0]['content'])

        dicto['language'] = 'pt-BR'
        results = subtitleseeker.response(response)
        self.assertEqual(results[0]['url'], 'http://this.is.the.url/Brazilian/')

        html = """
        <div class="boxRows">
            <div class="boxRowsInner" style="width:600px;">
                <img src="http://static.subtitleseeker.com/images/movie.gif"
                    style="width:16px; height:16px;" class="icon">
                <a href="http://this.is.the.url/"
                    class="blue" title="Title subtitle" >
                    This is the Title
                </a>
            </div>
            <div class="boxRowsInner f12b red" style="width:70px;">
                1998
            </div>
            <div class="boxRowsInner grey-web f12" style="width:120px;">
                <img src="http://static.subtitleseeker.com/images/basket_put.png"
                    style="width:16px; height:16px;" class="icon">
                1039 Subs
            </div>
            <div class="boxRowsInner grey-web f10" style="width:130px;">
                <img src="http://static.subtitleseeker.com/images/arrow_refresh_small.png"
                    style="width:16px; height:16px;" class="icon">
                1 hours ago
            </div>
            <div class="clear"></div>
        </div>
        """
        dicto['language'] = 'all'
        response = mock.Mock(text=html, search_params=dicto)
        results = subtitleseeker.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the Title')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url/')
        self.assertIn('1998', results[0]['content'])
        self.assertIn('1039 Subs', results[0]['content'])

        html = """
        <div class="boxRows">
            <div class="boxRowsInner" style="width:600px;">
                <img src="http://static.subtitleseeker.com/images/movie.gif"
                    style="width:16px; height:16px;" class="icon">
                <a href="http://this.is.the.url/"
                    class="blue" title="Title subtitle" >
                    This is the Title
                </a>
            </div>
            <div class="boxRowsInner f12b red" style="width:70px;">
                1998
            </div>
            <div class="boxRowsInner grey-web f12" style="width:120px;">
                <img src="http://static.subtitleseeker.com/images/basket_put.png"
                    style="width:16px; height:16px;" class="icon">
                1039 Subs
            </div>
            <div class="boxRowsInner grey-web f10" style="width:130px;">
                <img src="http://static.subtitleseeker.com/images/arrow_refresh_small.png"
                    style="width:16px; height:16px;" class="icon">
                1 hours ago
            </div>
            <div class="clear"></div>
        </div>
        """
        subtitleseeker.language = 'English'
        response = mock.Mock(text=html, search_params=dicto)
        results = subtitleseeker.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the Title')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url/English/')
        self.assertIn('1998', results[0]['content'])
        self.assertIn('1039 Subs', results[0]['content'])

        html = """
        <div class="boxRowsInner" style="width:600px;">
            <img src="http://static.subtitleseeker.com/images/movie.gif"
                style="width:16px; height:16px;" class="icon">
            <a href="http://this.is.the.url/"
                class="blue" title="Title subtitle" >
                This is the Title
            </a>
        </div>
        <div class="boxRowsInner f12b red" style="width:70px;">
            1998
        </div>
        <div class="boxRowsInner grey-web f12" style="width:120px;">
            <img src="http://static.subtitleseeker.com/images/basket_put.png"
                style="width:16px; height:16px;" class="icon">
            1039 Subs
        </div>
        <div class="boxRowsInner grey-web f10" style="width:130px;">
            <img src="http://static.subtitleseeker.com/images/arrow_refresh_small.png"
                style="width:16px; height:16px;" class="icon">
            1 hours ago
        </div>
        """
        response = mock.Mock(text=html, search_params=dicto)
        results = subtitleseeker.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
