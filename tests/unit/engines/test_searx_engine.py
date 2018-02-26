from collections import defaultdict
import mock
from searx.engines import searx_engine
from searx.testing import SearxTestCase


class TestSearxEngine(SearxTestCase):
    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['method'] = 'GET'
        dicto['category'] = 'music'
        dicto['time_rage'] = '0:0'
        dicto['language'] = 'en'

        searx_engine.instance_index = 1
        searx_engine.instance_urls = ['test_url']

        req = searx_engine.request(query, dicto)
        self.assertEqual(req['data']['pageno'], 1)
        self.assertEqual(req['method'], 'POST')
        self.assertEqual(req['data']['language'], 'en')
        self.assertEqual(req['data']['category'], 'music')

    def test_response(self):
        text_params = '{"results": [], ' \
                      '"answers":[], ' \
                      '"infoboxes": [2], ' \
                      '"suggestions": [2], ' \
                      '"number_of_results": [2,3]}'

        response = mock.Mock(text=text_params)
        resp = searx_engine.response(response)

        self.assertEqual(resp[0], 2)
        self.assertEqual(resp[1]['suggestion'], 2)
        self.assertEqual(resp[2]['number_of_results'], [2, 3])

    def test_multiple_suggestions_response(self):
        text_params = '{"results": [], ' \
                      '"answers":[], ' \
                      '"infoboxes": [2], ' \
                      '"suggestions": [2,3], ' \
                      '"number_of_results": [2,3]}'

        response = mock.Mock(text=text_params)
        resp = searx_engine.response(response)

        self.assertEqual(resp[0], 2)
        self.assertEqual(resp[1]['suggestion'], 2)
        self.assertEqual(resp[2]['suggestion'], 3)
        self.assertEqual(resp[3]['number_of_results'], [2, 3])

    def test_multiple_answers_response(self):
        text_params = '{"results": [], ' \
                      '"answers":["ans1", "ans2"], ' \
                      '"infoboxes": [2], ' \
                      '"suggestions": [], ' \
                      '"number_of_results": [2,3]}'

        response = mock.Mock(text=text_params)
        resp = searx_engine.response(response)

        self.assertEqual(resp[0], 'ans1')
        self.assertEqual(resp[1], 'ans2')
        self.assertEqual(resp[2], 2)
        self.assertEqual(resp[3]['number_of_results'], [2, 3])
