# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import openairedatasets
from searx.testing import SearxTestCase


class TestOpenairedatasetsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = openairedatasets.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn('api.openaire.eu', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, openairedatasets.response, None)
        self.assertRaises(AttributeError, openairedatasets.response, [])
        self.assertRaises(AttributeError, openairedatasets.response, '')
        self.assertRaises(AttributeError, openairedatasets.response, '[]')

        response = mock.Mock(text='{"response":{"results":{"result":[]}}}')
        self.assertEqual(openairedatasets.response(response), [])

        json_mock = '''{
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
      "fields": null
    },
    "results": {
      "result": [{
        "metadata": {
          "oaf:entity": {
            "@xsi:schemaLocation": "http://namespace.openaire.eu/oaf https://www.openaire.eu/schema/0.3/oaf-0.3.xsd",
            "oaf:result": {
              "description": {
                "$": "The data from the experiment."
              },
              "title": {
                "$": "Experimental data."
              },
              "dateofacceptance": {
                "$": "2000-01-01"
              },
              "size": null,
              "format": null,
              "publisher": {
                "$": "Zenodo"
              },
              "subject": [
                {
                  "@classid": "keyword",
                  "$": "Data"
                }
              ],
              "embargoenddate": null,
              "fulltext": null,
              "originalId": [
                {
                  "$": "10.1000/xyz123"
                }
              ],
              "pid": {
                "@classid": "doi",
                "$": "10.1000/xyz123"
              },
              "children": {
                "instance": {
                  "webresource": {
                    "url": {
                      "$": "http://dx.doi.org/10.1000/xyz123"
                    }
                  }
                }
              }}
            }
          }
        }
      ]
    }
  }
}
'''
        response = mock.Mock(text=json_mock)
        results = openairedatasets.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
