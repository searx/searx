# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import pubmed
from searx.testing import SearxTestCase


class TestPubmedEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = pubmed.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn('eutils.ncbi.nlm.nih.gov/', params['url'])
        self.assertIn('term', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, pubmed.response, None)
        self.assertRaises(AttributeError, pubmed.response, [])
        self.assertRaises(AttributeError, pubmed.response, '')
        self.assertRaises(AttributeError, pubmed.response, '[]')

        response = mock.Mock(text='<PubmedArticleSet></PubmedArticleSet>')
        self.assertEqual(pubmed.response(response), [])

        xml_mock = """<eSearchResult><Count>1</Count><RetMax>1</RetMax><RetStart>0</RetStart><IdList>
<Id>1</Id>
</IdList></eSearchResult>
"""

        response = mock.Mock(text=xml_mock.encode('utf-8'))
        results = pubmed.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], 'No abstract is available for this publication.')
