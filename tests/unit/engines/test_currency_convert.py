from collections import defaultdict
from datetime import datetime
import mock
from searx.engines import currency_convert
from searx.testing import SearxTestCase


class TestCurrencyConvertEngine(SearxTestCase):

    def test_request(self):
        query = b'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = currency_convert.request(query, dicto)
        self.assertNotIn('url', params)

        query = b'convert 10 Pound Sterlings to United States Dollars'
        params = currency_convert.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn('finance.yahoo.com', params['url'])
        self.assertIn('GBP', params['url'])
        self.assertIn('USD', params['url'])

    def test_response(self):
        dicto = defaultdict(dict)
        dicto['ammount'] = float(10)
        dicto['from'] = "GBP"
        dicto['to'] = "USD"
        dicto['from_name'] = "pound sterling"
        dicto['to_name'] = "United States dollar"
        response = mock.Mock(text='a,b,c,d', search_params=dicto)
        self.assertEqual(currency_convert.response(response), [])

        csv = "2,0.5,1"
        response = mock.Mock(text=csv, search_params=dicto)
        results = currency_convert.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['answer'], '10.0 GBP = 5.0 USD, 1 GBP (pound sterling)' +
                         ' = 0.5 USD (United States dollar)')
        now_date = datetime.now().strftime('%Y%m%d')
        self.assertEqual(results[0]['url'], 'https://finance.yahoo.com/currency/converter-results/' +
                                            now_date + '/10.0-gbp-to-usd.html')
