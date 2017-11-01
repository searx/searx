# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import openairepublications
from searx.testing import SearxTestCase


class TestOpenairepublicationsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = openairepublications.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn('api.openaire.eu', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, openairepublications.response, None)
        self.assertRaises(AttributeError, openairepublications.response, [])
        self.assertRaises(AttributeError, openairepublications.response, '')
        self.assertRaises(AttributeError, openairepublications.response, '[]')

        response = mock.Mock(text='{"response":{"results":{"result":[]}}}')
        self.assertEqual(openairepublications.response(response), [])

        json_mock = '''
{
  "response": {
    "header": {
      "query": {
        "$": "(oaftype exact result) and (resulttypeid exact dataset) and (test_query)"
      },
      "locale": {
        "$": "en_US"
      },
      "size": {
        "$": 1
      },
      "page": {
        "$": 1
      },
      "total": {
        "$": 1
      },
      "fields": "null"
    },
    "results": {
      "result": [{
        "metadata": {
          "oaf:entity": {
            "@xsi:schemaLocation": "http://namespace.openaire.eu/oaf https://www.openaire.eu/schema/0.3/oaf-0.3.xsd",
            "oaf:result": {
              "description": {
                "$": "Some scientific results."
              },
              "title": {
                "$": "Results of an experiment."
              },
              "version": "null",
              "dateofacceptance": {
                "$": "2000-01-01"
              },
              "publisher": {
                "$": "ArXiV"
              },
              "subject": [
                {
                "$": "Science"
                }
              ],
              "embargoenddate": "null",
              "source": "null",
              "fulltext": "null",
              "originalId": [
                {
                  "$": "10.1000/xyz123"
                }
              ],
              "pid": {
                "@classid": "doi",
                "@classname": "doi",
                "@schemeid": "dnet:pid_types",
                "@schemename": "dnet:pid_types",
                "$": "10.1000/xyz123"
              },
              "bestlicense": {
                "@classid": "UNKNOWN",
                "@classname": "not available",
                "@schemeid": "dnet:access_modes",
                "@schemename": "dnet:access_modes"
              },
              "children": {
                "instance": {
                  "webresource": {
                    "url": {
                      "$": "http://doi.org/10.1000/xyz123"
                    }
                  }
                }}
              }
            }
          }
        }
      ]
    }
  }
}
'''
        response = mock.Mock(text=json_mock.encode('utf-8'))
        results = openairepublications.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Results of an experiment.')
        self.assertEqual(results[0]['url'], 'http://doi.org/10.1000/xyz123')
        self.assertEqual(results[0]['content'], 'Some scientific results.')
