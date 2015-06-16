# -*- coding: utf-8 -*-

from searx.search import score_results
from searx.testing import SearxTestCase


def fake_result(url='https://aa.bb/cc?dd=ee#ff',
                title='aaa',
                content='bbb',
                engine='wikipedia'):
    return {'url': url,
            'title': title,
            'content': content,
            'engine': engine}


class ScoreResultsTestCase(SearxTestCase):

    def test_empty(self):
        self.assertEqual(score_results(dict()), [])

    def test_urlparse(self):
        results = score_results(dict(a=[fake_result(url='https://aa.bb/cc?dd=ee#ff')]))
        parsed_url = results[0]['parsed_url']
        self.assertEqual(parsed_url.query, 'dd=ee')
