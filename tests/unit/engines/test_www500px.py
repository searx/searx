# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import www500px
from searx.testing import SearxTestCase


class TestWww500pxImagesEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = www500px.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('500px.com' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, www500px.response, None)
        self.assertRaises(AttributeError, www500px.response, [])
        self.assertRaises(AttributeError, www500px.response, '')
        self.assertRaises(AttributeError, www500px.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(www500px.response(response), [])

        html = """
        <div class="photo">
            <a href="/this.should.be.the.url" data-ga-category="Photo Thumbnail" data-ga-action="Title">
                <img src="https://image.url/3.jpg?v=0" />
            </a>
            <div class="details">
                <div class="inside">
                    <div class="title">
                        <a href="/photo/64312705/branch-out-by-oliver-turpin?feature=">
                            This is the title
                        </a>
                    </div>
                    <div class="info">
                        <a href="/ChronicleUK" data-ga-action="Image" data-ga-category="Photo Thumbnail">
                            This is the content
                        </a>
                    </div>
                    <div class="rating">44.8</div>
                </div>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = www500px.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://500px.com/this.should.be.the.url')
        self.assertEqual(results[0]['content'], 'This is the content')
        self.assertEqual(results[0]['thumbnail_src'], 'https://image.url/3.jpg?v=0')
        self.assertEqual(results[0]['img_src'], 'https://image.url/2048.jpg')

        html = """
        <a href="/this.should.be.the.url" data-ga-category="Photo Thumbnail" data-ga-action="Title">
            <img src="https://image.url/3.jpg?v=0" />
        </a>
        <div class="details">
            <div class="inside">
                <div class="title">
                    <a href="/photo/64312705/branch-out-by-oliver-turpin?feature=">
                        This is the title
                    </a>
                </div>
                <div class="info">
                    <a href="/ChronicleUK" data-ga-action="Image" data-ga-category="Photo Thumbnail">
                        Oliver Turpin
                    </a>
                </div>
                <div class="rating">44.8</div>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = www500px.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
