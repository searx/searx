from collections import defaultdict
import mock
from searx.engines import scanr_structures
from searx.testing import SearxTestCase


class TestScanrStructuresEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = scanr_structures.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['data'])
        self.assertIn('scanr.enseignementsup-recherche.gouv.fr', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, scanr_structures.response, None)
        self.assertRaises(AttributeError, scanr_structures.response, [])
        self.assertRaises(AttributeError, scanr_structures.response, '')
        self.assertRaises(AttributeError, scanr_structures.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(scanr_structures.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(scanr_structures.response(response), [])

        json = u"""
        {
          "request":
            {
              "query":"test_query",
              "page":1,
              "pageSize":20,
              "sortOrder":"RELEVANCY",
              "sortDirection":"ASC",
              "searchField":"ALL",
              "from":0
            },
          "total":2471,
          "results":[
            {
              "id":"200711886U",
              "label":"Laboratoire d'Informatique de Grenoble",
              "kind":"RNSR",
              "publicEntity":true,
              "address":{"city":"Grenoble","departement":"38"},
              "logo":"/static/logos/200711886U.png",
              "acronym":"LIG",
              "type":{"code":"UR","label":"Unit\xe9 de recherche"},
              "level":2,
              "institutions":[
                {
                  "id":"193819125",
                  "label":"Grenoble INP",
                  "acronym":"IPG",
                  "code":"UMR 5217"
                },
                {
                  "id":"130021397",
                  "label":"Universit\xe9 de Grenoble Alpes",
                  "acronym":"UGA",
                  "code":"UMR 5217"
                },
                {
                  "id":"180089013",
                  "label":"Centre national de la recherche scientifique",
                  "acronym":"CNRS",
                  "code":"UMR 5217"
                },
                {
                  "id":"180089047",
                  "label":"Institut national de recherche en informatique et en automatique",
                  "acronym":"Inria",
                  "code":"UMR 5217"
                }
              ],
              "highlights":[
                {
                  "type":"projects",
                  "value":"linguicielles d\xe9velopp\xe9s jusqu'ici par le GETALP\
 du <strong>LIG</strong> en tant que prototypes op\xe9rationnels.\
\\r\\nDans le contexte"
                },
                {
                  "type":"acronym",
                  "value":"<strong>LIG</strong>"
                },
                {
                  "type":"websiteContents",
                  "value":"S\xe9lection\\nListe structures\\nD\xe9tail\\n\
                    Accueil\\n200711886U : <strong>LIG</strong>\
                    Laboratoire d'Informatique de Grenoble Unit\xe9 de recherche"},
                {
                  "type":"publications",
                  "value":"de noms. Nous avons d'abord d\xe9velopp\xe9 LOOV \
                    (pour <strong>Lig</strong> Overlaid OCR in Vid\xe9o), \
                    un outil d'extraction des"
                }
              ]
            },
            {
              "id":"199511665F",
              "label":"Laboratoire Bordelais de Recherche en Informatique",
              "kind":"RNSR",
              "publicEntity":true,
              "address":{"city":"Talence","departement":"33"},
              "logo":"/static/logos/199511665F.png",
              "acronym":"LaBRI",
              "type":{"code":"UR","label":"Unit\xe9 de recherche"},
              "level":2,
              "institutions":[
                {
                  "id":"130006356",
                  "label":"Institut polytechnique de Bordeaux",
                  "acronym":"IPB",
                  "code":"UMR 5800"
                },
                {
                  "id":"130018351",
                  "label":"Universit\xe9 de Bordeaux",
                  "acronym":null,
                  "code":"UMR 5800"
                },
                {
                  "id":"180089013",
                  "label":"Centre national de la recherche scientifique",
                  "acronym":"CNRS",
                  "code":"UMR 5800"
                },
                {
                  "id":"180089047",
                  "label":"Institut national de recherche en informatique et en automatique",
                  "acronym":"Inria",
                  "code":"UMR 5800"
                }
              ],
              "highlights":[
                {
                  "type":"websiteContents",
                  "value":"Samia Kerdjoudj\\n2016-07-05\\nDouble-exponential\
 and <strong>triple</strong>-exponential bounds for\
 choosability problems parameterized"
                },
                {
                  "type":"publications",
                  "value":"de cam\xe9ras install\xe9es dans les lieux publiques \
 a <strong>tripl\xe9</strong> en 2009, passant de 20 000 \
 \xe0 60 000. Malgr\xe9 le"
                }
              ]
            }
          ]
        }
        """
        response = mock.Mock(text=json)
        results = scanr_structures.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], u"Laboratoire d'Informatique de Grenoble")
        self.assertEqual(results[0]['url'], 'https://scanr.enseignementsup-recherche.gouv.fr/structure/200711886U')
        self.assertEqual(results[0]['content'],
                         u"linguicielles d\xe9velopp\xe9s jusqu'ici par le GETALP "
                         u"du LIG en tant que prototypes "
                         u"op\xe9rationnels. Dans le contexte")
        self.assertEqual(results[1]['img_src'],
                         'https://scanr.enseignementsup-recherche.gouv.fr//static/logos/199511665F.png')
        self.assertEqual(results[1]['content'],
                         "Samia Kerdjoudj 2016-07-05 Double-exponential and"
                         " triple-exponential bounds for "
                         "choosability problems parameterized")
        self.assertEqual(results[1]['url'], 'https://scanr.enseignementsup-recherche.gouv.fr/structure/199511665F')
        self.assertEqual(results[1]['title'], u"Laboratoire Bordelais de Recherche en Informatique")
