from collections import defaultdict
import mock
from searx.engines import duckduckgo_definitions
from searx.testing import SearxTestCase


class TestDDGDefinitionsEngine(SearxTestCase):

    def test_result_to_text(self):
        url = ''
        text = 'Text'
        html_result = 'Html'
        result = duckduckgo_definitions.result_to_text(url, text, html_result)
        self.assertEqual(result, text)

        html_result = '<a href="url">Text in link</a>'
        result = duckduckgo_definitions.result_to_text(url, text, html_result)
        self.assertEqual(result, 'Text in link')

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'es'
        params = duckduckgo_definitions.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('duckduckgo.com', params['url'])
        self.assertIn('headers', params)
        self.assertIn('Accept-Language', params['headers'])
        self.assertIn('es', params['headers']['Accept-Language'])

    def test_response(self):
        self.assertRaises(AttributeError, duckduckgo_definitions.response, None)
        self.assertRaises(AttributeError, duckduckgo_definitions.response, [])
        self.assertRaises(AttributeError, duckduckgo_definitions.response, '')
        self.assertRaises(AttributeError, duckduckgo_definitions.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(duckduckgo_definitions.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(duckduckgo_definitions.response(response), [])

        json = """
        {
          "DefinitionSource": "definition source",
          "Heading": "heading",
          "ImageWidth": 0,
          "RelatedTopics": [
            {
              "Result": "Top-level domains",
              "Icon": {
                "URL": "",
                "Height": "",
                "Width": ""
              },
              "FirstURL": "https://first.url",
              "Text": "text"
            },
            {
              "Topics": [
                {
                  "Result": "result topic",
                  "Icon": {
                    "URL": "",
                    "Height": "",
                    "Width": ""
                  },
                  "FirstURL": "https://duckduckgo.com/?q=2%2F2",
                  "Text": "result topic text"
                }
              ],
              "Name": "name"
            }
          ],
          "Entity": "Entity",
          "Type": "A",
          "Redirect": "",
          "DefinitionURL": "http://definition.url",
          "AbstractURL": "https://abstract.url",
          "Definition": "this is the definition",
          "AbstractSource": "abstract source",
          "Infobox": {
            "content": [
              {
                "data_type": "string",
                "value": "1999",
                "label": "Introduced",
                "wiki_order": 0
              }
            ],
            "meta": [
              {
                "data_type": "string",
                "value": ".test",
                "label": "article_title"
              }
            ]
          },
          "Image": "image.png",
          "ImageIsLogo": 0,
          "Abstract": "abstract",
          "AbstractText": "abstract text",
          "AnswerType": "",
          "ImageHeight": 0,
          "Results": [{
                 "Result" : "result title",
                 "Icon" : {
                    "URL" : "result url",
                    "Height" : 16,
                    "Width" : 16
                 },
                 "FirstURL" : "result first url",
                 "Text" : "result text"
              }
          ],
          "Answer": "answer"
        }
        """
        response = mock.Mock(text=json)
        results = duckduckgo_definitions.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]['answer'], 'answer')
        self.assertEqual(results[1]['title'], 'heading')
        self.assertEqual(results[1]['url'], 'result first url')
        self.assertEqual(results[2]['suggestion'], 'text')
        self.assertEqual(results[3]['infobox'], 'heading')
        self.assertEqual(results[3]['id'], 'https://definition.url')
        self.assertEqual(results[3]['entity'], 'Entity')
        self.assertIn('abstract', results[3]['content'])
        self.assertIn('this is the definition', results[3]['content'])
        self.assertEqual(results[3]['img_src'], 'image.png')
        self.assertIn('Introduced', results[3]['attributes'][0]['label'])
        self.assertIn('1999', results[3]['attributes'][0]['value'])
        self.assertIn({'url': 'https://abstract.url', 'title': 'abstract source'}, results[3]['urls'])
        self.assertIn({'url': 'http://definition.url', 'title': 'definition source'}, results[3]['urls'])
        self.assertIn({'name': 'name', 'suggestions': ['result topic text']}, results[3]['relatedTopics'])

        json = """
        {
          "DefinitionSource": "definition source",
          "Heading": "heading",
          "ImageWidth": 0,
          "RelatedTopics": [],
          "Entity": "Entity",
          "Type": "A",
          "Redirect": "",
          "DefinitionURL": "",
          "AbstractURL": "https://abstract.url",
          "Definition": "",
          "AbstractSource": "abstract source",
          "Image": "",
          "ImageIsLogo": 0,
          "Abstract": "",
          "AbstractText": "abstract text",
          "AnswerType": "",
          "ImageHeight": 0,
          "Results": [],
          "Answer": ""
        }
        """
        response = mock.Mock(text=json)
        results = duckduckgo_definitions.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['url'], 'https://abstract.url')
        self.assertEqual(results[0]['title'], 'heading')
        self.assertEqual(results[0]['content'], '')

        json = """
        {
          "DefinitionSource": "definition source",
          "Heading": "heading",
          "ImageWidth": 0,
          "RelatedTopics": [
            {
              "Result": "Top-level domains",
              "Icon": {
                "URL": "",
                "Height": "",
                "Width": ""
              },
              "FirstURL": "https://first.url",
              "Text": "heading"
            },
            {
              "Name": "name"
            },
            {
              "Topics": [
                {
                  "Result": "result topic",
                  "Icon": {
                    "URL": "",
                    "Height": "",
                    "Width": ""
                  },
                  "FirstURL": "https://duckduckgo.com/?q=2%2F2",
                  "Text": "heading"
                }
              ],
              "Name": "name"
            }
          ],
          "Entity": "Entity",
          "Type": "A",
          "Redirect": "",
          "DefinitionURL": "http://definition.url",
          "AbstractURL": "https://abstract.url",
          "Definition": "this is the definition",
          "AbstractSource": "abstract source",
          "Infobox": {
            "meta": [
              {
                "data_type": "string",
                "value": ".test",
                "label": "article_title"
              }
            ]
          },
          "Image": "image.png",
          "ImageIsLogo": 0,
          "Abstract": "abstract",
          "AbstractText": "abstract text",
          "AnswerType": "",
          "ImageHeight": 0,
          "Results": [{
                 "Result" : "result title",
                 "Icon" : {
                    "URL" : "result url",
                    "Height" : 16,
                    "Width" : 16
                 },
                 "Text" : "result text"
              }
          ],
          "Answer": ""
        }
        """
        response = mock.Mock(text=json)
        results = duckduckgo_definitions.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['infobox'], 'heading')
        self.assertEqual(results[0]['id'], 'https://definition.url')
        self.assertEqual(results[0]['entity'], 'Entity')
        self.assertIn('abstract', results[0]['content'])
        self.assertIn('this is the definition', results[0]['content'])
        self.assertEqual(results[0]['img_src'], 'image.png')
        self.assertIn({'url': 'https://abstract.url', 'title': 'abstract source'}, results[0]['urls'])
        self.assertIn({'url': 'http://definition.url', 'title': 'definition source'}, results[0]['urls'])
        self.assertIn({'name': 'name', 'suggestions': []}, results[0]['relatedTopics'])
