# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import vimeo
from searx.testing import SearxTestCase


class TestVimeoEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = vimeo.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('vimeo.com' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, vimeo.response, None)
        self.assertRaises(AttributeError, vimeo.response, [])
        self.assertRaises(AttributeError, vimeo.response, '')
        self.assertRaises(AttributeError, vimeo.response, '[]')

        json = u"""
{"filtered":{"total":274641,"page":1,"per_page":18,"paging":{"next":"?sizes=590x332&page=2","previous":null,"first":"?sizes=590x332&page=1","last":"?sizes=590x332&page=15258"},"data":[{"is_staffpick":false,"is_featured":true,"type":"clip","clip":{"uri":"\\/videos\\/106557563","name":"Hot Rod Revue: The South","link":"https:\\/\\/vimeo.com\\/106557563","duration":4069,"created_time":"2014-09-19T03:38:04+00:00","privacy":{"view":"ptv"},"pictures":{"sizes":[{"width":"590","height":"332","link":"https:\\/\\/i.vimeocdn.com\\/video\\/489717884_590x332.jpg?r=pad","link_with_play_button":"https:\\/\\/i.vimeocdn.com\\/filter\\/overlay?src0=https%3A%2F%2Fi.vimeocdn.com%2Fvideo%2F489717884_590x332.jpg&src1=http%3A%2F%2Ff.vimeocdn.com%2Fp%2Fimages%2Fcrawler_play.png"}]},"stats":{"plays":null},"metadata":{"connections":{"comments":{"total":0},"likes":{"total":5}},"interactions":[]},"user":{"name":"Cal Thorley","link":"https:\\/\\/vimeo.com\\/calthorley","pictures":{"sizes":[{"width":30,"height":30,"link":"https:\\/\\/i.vimeocdn.com\\/portrait\\/2545308_30x30?r=pad"},{"width":75,"height":75,"link":"https:\\/\\/i.vimeocdn.com\\/portrait\\/2545308_75x75?r=pad"},{"width":100,"height":100,"link":"https:\\/\\/i.vimeocdn.com\\/portrait\\/2545308_100x100?r=pad"},{"width":300,"height":300,"link":"https:\\/\\/i.vimeocdn.com\\/portrait\\/2545308_300x300?r=pad"}]}}}}]}};

"""  # noqa
        response = mock.Mock(text=json)
        results = vimeo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], u'Hot Rod Revue: The South')
        self.assertEqual(results[0]['url'], 'https://vimeo.com/106557563')
        self.assertEqual(results[0]['content'], '')
        self.assertEqual(results[0]['thumbnail'], 'https://i.vimeocdn.com/video/489717884_590x332.jpg?r=pad')
