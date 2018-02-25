from searx.testing import SearxTestCase
import searx.poolrequests as requests_lib
from searx.engines import searx_engine
from searx.results import ResultContainer
from mock import MagicMock
from searx import search
from searx.query import SearchQuery
from searx.url_utils import ParseResult
from mock import Mock , mock
from time import time
from searx.answerers import ask


class FakeSearch():
  def __init__(self):
    super(FakeSearch, self).__init__()
    self.search_query = self.querys_Container()
    self.result_container = self.resultsContainer()

  def resultsContainer(self):

    self.example_results = [
            {
                'content': 'first thing content',
                'title': 'First Thing',
                'url': 'http://something1.test.com',
                'engines': ['bing'],
                'engine': 'bing',
                'parsed_url': ParseResult(scheme='http', netloc='something1.test.com', path='/', params='', query='', fragment=''),  
            }, {
                'content': 'second thing content',
                'title': 'Second Thing',
                'url': 'http://something2.test.com',
                'engines': ['youtube'],
                'engine': 'youtube',
                'parsed_url': ParseResult(scheme='http', netloc='something2.test.com', path='/', params='', query='', fragment=''),  
            },
        ]

    result_container = Mock(get_ordered_results=lambda: self.example_results,
                            answers=set(),
                            _merged_results= [],
                            corrections=set(),
                            suggestions=set(),
                            infoboxes=[],
                            unresponsive_engines=set(),
                            results=self.example_results,
                            _ordered = True,
                            paging = True,
                            results_number=lambda: 3,
                            results_length=lambda: len(self.example_results))
    
    ResultContainer.results = result_container


    return ResultContainer.results

  def querys_Container(self):

    query_container = Mock(query= 'something'.encode('utf-8'),
                           categories = ['general'],
                           engines = [{'category': 'general', 'name': 'wikipedia'}, {'category': 'general', 'name': 'bing'}, {'category': 'general', 'name': 'currency'}, {'category': 'general', 'name': 'wikidata'}, {'category': 'general', 'name': 'google'}, {'category': 'general', 'name': 'dictzone'}],
                           lang = 'all',
                           pageno = 1,
                           time_range = 0)

    SearchQuery.query = query_container                 

    return SearchQuery.query


class SearchTestCase(SearxTestCase):

    def test_search_instance(self):

      search_Container = FakeSearch()

      number_of_searches = None
      start_time = time()
      answerers_results = ask(search_Container.search_query)

      print(search_Container.search_query.engines)
      print(answerers_results)
      if answerers_results:
        self.assertEqual(search_Container.result_container.paging, False)


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
