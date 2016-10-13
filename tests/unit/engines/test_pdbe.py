import mock
from collections import defaultdict
from searx.engines import pdbe
from searx.testing import SearxTestCase


class TestPdbeEngine(SearxTestCase):
    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        params = pdbe.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue('ebi.ac.uk' in params['url'])
        self.assertTrue('data' in params)
        self.assertTrue('q' in params['data'])
        self.assertTrue(query in params['data']['q'])
        self.assertTrue('wt' in params['data'])
        self.assertTrue('json' in params['data']['wt'])
        self.assertTrue('method' in params)
        self.assertTrue(params['method'] == 'POST')

    def test_response(self):
        self.assertRaises(AttributeError, pdbe.response, None)
        self.assertRaises(AttributeError, pdbe.response, [])
        self.assertRaises(AttributeError, pdbe.response, '')
        self.assertRaises(AttributeError, pdbe.response, '[]')

        json = """
{
  "response": {
    "docs": [
      {
        "citation_title": "X-ray crystal structure of ferric Aplysia limacina myoglobin in different liganded states.",
        "citation_year": 1993,
        "entry_author_list": [
          "Conti E, Moser C, Rizzi M, Mattevi A, Lionetti C, Coda A, Ascenzi P, Brunori M, Bolognesi M"
        ],
        "journal": "J. Mol. Biol.",
        "journal_page": "498-508",
        "journal_volume": "233",
        "pdb_id": "2fal",
        "status": "REL",
        "title": "X-RAY CRYSTAL STRUCTURE OF FERRIC APLYSIA LIMACINA MYOGLOBIN IN DIFFERENT LIGANDED STATES"
      }
    ],
    "numFound": 1,
    "start": 0
  },
  "responseHeader": {
    "QTime": 0,
    "params": {
      "q": "2fal",
      "wt": "json"
    },
    "status": 0
  }
}
"""

        response = mock.Mock(text=json)
        results = pdbe.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'],
                         'X-RAY CRYSTAL STRUCTURE OF FERRIC APLYSIA LIMACINA MYOGLOBIN IN DIFFERENT LIGANDED STATES')
        self.assertEqual(results[0]['url'], pdbe.pdbe_entry_url.format(pdb_id='2fal'))
        self.assertEqual(results[0]['img_src'], pdbe.pdbe_preview_url.format(pdb_id='2fal'))
        self.assertTrue('Conti E' in results[0]['content'])
        self.assertTrue('X-ray crystal structure of ferric Aplysia limacina myoglobin in different liganded states.' in
                        results[0]['content'])
        self.assertTrue('1993' in results[0]['content'])

        # Testing proper handling of PDB entries marked as obsolete
        json = """
{
  "response": {
    "docs": [
      {
        "citation_title": "Obsolete entry test",
        "citation_year": 2016,
        "entry_author_list": ["Doe J"],
        "journal": "J. Obs.",
        "journal_page": "1-2",
        "journal_volume": "1",
        "pdb_id": "xxxx",
        "status": "OBS",
        "title": "OBSOLETE ENTRY TEST",
        "superseded_by": "yyyy"
      }
    ],
    "numFound": 1,
    "start": 0
  },
  "responseHeader": {
    "QTime": 0,
    "params": {
      "q": "xxxx",
      "wt": "json"
    },
    "status": 0
  }
}
"""
        response = mock.Mock(text=json)
        results = pdbe.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'OBSOLETE ENTRY TEST&nbsp;(OBSOLETE)')
        self.assertTrue(results[0]['content'].startswith('<em>This entry has been superseded by'))
