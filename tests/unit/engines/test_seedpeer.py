import mock
from collections import defaultdict
from searx.engines import seedpeer
from searx.testing import SearxTestCase
from datetime import datetime


class TestSeedPeerEngine(SearxTestCase):

    html = ''
    with open('./tests/unit/engines/seedpeer_fixture.html') as fixture:
        html += fixture.read()

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = seedpeer.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('seedpeer.eu', params['url'])

    def test_response_raises_attr_error_on_empty_response(self):
        self.assertRaises(AttributeError, seedpeer.response, None)
        self.assertRaises(AttributeError, seedpeer.response, [])
        self.assertRaises(AttributeError, seedpeer.response, '')
        self.assertRaises(AttributeError, seedpeer.response, '[]')

    def test_response_returns_empty_list(self):
        response = mock.Mock(text='<html></html>')
        self.assertEqual(seedpeer.response(response), [])

    def test_response_returns_all_results(self):
        response = mock.Mock(text=self.html)
        results = seedpeer.response(response)
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 2)

    def test_response_returns_correct_results(self):
        response = mock.Mock(text=self.html)
        results = seedpeer.response(response)
        self.assertEqual(
            results[0]['title'], 'Narcos - Season 2 - 720p WEBRiP - x265 HEVC - ShAaNiG '
        )
        self.assertEqual(
            results[0]['url'],
            'http://www.seedpeer.eu/details/11685972/Narcos---Season-2---720p-WEBRiP---x265-HEVC---ShAaNiG.html'
        )
        self.assertEqual(results[0]['content'], '2.48 GB, 1 day')
        self.assertEqual(results[0]['seed'], '861')
        self.assertEqual(results[0]['leech'], '332')
