from searx.testing import SearxTestCase
import searx.poolrequests as requests_lib
from searx.engines import searx_engine
from mock import MagicMock
from searx import search
import mock


class SearchTestCase(SearxTestCase):
    def test_send_http_request_method_post(self):
        request_args = dict(
            headers="test_headers",
            cookies="test_cookies",
            verify="test_verify",
            data="test_data"
        )

        request_params = {"headers": "test_headers",
                          "method": "POST",
                          "cookies": "test_cookies",
                          "verify": "test_verify",
                          "data": "test_data",
                          "url": "test_url"}

        mocked_request_lib_post = requests_lib
        mocked_request_lib_post.post = MagicMock(return_value='post_req')
        req = search.send_http_request(None, request_params)

        mocked_request_lib_post.post.assert_called_with(
            'test_url', **request_args)
        self.assertEqual(req, 'post_req')

    def test_send_http_request_method_get(self):
        request_args = dict(
            headers="test_headers",
            cookies="test_cookies",
            verify="test_verify",
        )

        request_params = {"headers": "test_headers",
                          "method": "GET",
                          "cookies": "test_cookies",
                          "verify": "test_verify",
                          "data": "test_data",
                          "url": "test_url"}

        mocked_request_lib_get = requests_lib
        mocked_request_lib_get.get = MagicMock(return_value='get_req')
        res = search.send_http_request(None, request_params)

        mocked_request_lib_get.get.assert_called_with(
            'test_url', **request_args)
        self.assertEqual(res, 'get_req')

    def test_search_one_request_empty_request_params(self):
        mocked_searx_engine = searx_engine
        mocked_searx_engine.request = MagicMock(return_value='test')
        test_query = "test_query"
        request_params = {"url": None}

        res = search.search_one_request(
            mocked_searx_engine, test_query, request_params)

        self.assertEqual(res, [])
        mocked_searx_engine.request.assert_called_with(
            test_query, request_params)

    def test_search_one_request_not_empty_url(self):
        mocked_searx_engine = searx_engine
        mocked_searx_engine.request = MagicMock(return_value="test")
        mocked_searx_engine.response = MagicMock(return_value="test")
        mocked_request_lib_get = requests_lib

        text_params = '{"results": [], ' \
                      '"answers":[], ' \
                      '"infoboxes": [2], ' \
                      '"suggestions": [2], ' \
                      '"number_of_results": [2,3]}'

        response = mock.Mock(text=text_params, search_params={})
        mocked_request_lib_get.get = MagicMock(return_value=response)
        test_query = "test_query"
        request_params = {"headers": "test_headers",
                          "method": "GET",
                          "cookies": "test_cookies",
                          "verify": "test_verify",
                          "data": "test_data",
                          "url": "test_url"}

        request_args = dict(
            headers="test_headers",
            cookies="test_cookies",
            verify="test_verify",
        )

        res = search.search_one_request(
            mocked_searx_engine, test_query, request_params)

        self.assertEqual(res, 'test')
        mocked_searx_engine.request.assert_called_with(
            test_query, request_params)
        mocked_searx_engine.response.assert_called_with(response)
        mocked_request_lib_get.get.assert_called_with(
            "test_url", **request_args)

    def test_default_request_params(self):
        res = search.default_request_params()

        self.assertEqual(res['method'], 'GET')
        self.assertEqual(res['headers'], {})
        self.assertEqual(res['data'], {})
        self.assertEqual(res['url'], '')
        self.assertEqual(res['cookies'], {})
