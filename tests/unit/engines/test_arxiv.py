# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import arxiv
from searx.testing import SearxTestCase


class TestBaseEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'.encode('utf-8')
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = arxiv.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn('export.arxiv.org/api/', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, arxiv.response, None)
        self.assertRaises(AttributeError, arxiv.response, [])
        self.assertRaises(AttributeError, arxiv.response, '')
        self.assertRaises(AttributeError, arxiv.response, '[]')

        response = mock.Mock(content=b'''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"></feed>''')
        self.assertEqual(arxiv.response(response), [])

        xml_mock = b'''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title type="html">ArXiv Query: search_query=all:test_query&amp;id_list=&amp;start=0&amp;max_results=1</title>
  <id>http://arxiv.org/api/1</id>
  <updated>2000-01-21T00:00:00-01:00</updated>
  <opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">1</opensearch:totalResults>
  <opensearch:startIndex xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">0</opensearch:startIndex>
  <opensearch:itemsPerPage xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">1</opensearch:itemsPerPage>
  <entry>
    <id>http://arxiv.org/1</id>
    <updated>2000-01-01T00:00:01Z</updated>
    <published>2000-01-01T00:00:01Z</published>
    <title>Mathematical proof.</title>
    <summary>Mathematical formula.</summary>
    <author>
      <name>A. B.</name>
    </author>
    <link href="http://arxiv.org/1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/1" rel="related" type="application/pdf"/>
    <category term="math.QA" scheme="http://arxiv.org/schemas/atom"/>
    <category term="1" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>
'''

        response = mock.Mock(content=xml_mock)
        results = arxiv.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Mathematical proof.')
        self.assertEqual(results[0]['content'], 'Mathematical formula.')
