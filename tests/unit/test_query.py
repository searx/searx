from searx.query import RawTextQuery
from searx.testing import SearxTestCase


class TestQuery(SearxTestCase):

    def test_simple_query(self):
        query_text = 'the query'
        query = RawTextQuery(query_text, [])
        query.parse_query()

        self.assertEquals(query.getFullQuery(), query_text)
        self.assertEquals(len(query.query_parts), 1)
        self.assertEquals(len(query.languages), 0)
        self.assertFalse(query.specific)

    def test_language_code(self):
        language = 'es-ES'
        query_text = 'the query'
        full_query = ':' + language + ' ' + query_text
        query = RawTextQuery(full_query, [])
        query.parse_query()

        self.assertEquals(query.getFullQuery(), full_query)
        self.assertEquals(len(query.query_parts), 3)
        self.assertEquals(len(query.languages), 1)
        self.assertIn(language, query.languages)
        self.assertFalse(query.specific)

    def test_language_name(self):
        language = 'english'
        query_text = 'the query'
        full_query = ':' + language + ' ' + query_text
        query = RawTextQuery(full_query, [])
        query.parse_query()

        self.assertEquals(query.getFullQuery(), full_query)
        self.assertEquals(len(query.query_parts), 3)
        self.assertIn('en', query.languages)
        self.assertFalse(query.specific)

    def test_unlisted_language_code(self):
        language = 'all'
        query_text = 'the query'
        full_query = ':' + language + ' ' + query_text
        query = RawTextQuery(full_query, [])
        query.parse_query()

        self.assertEquals(query.getFullQuery(), full_query)
        self.assertEquals(len(query.query_parts), 3)
        self.assertIn('all', query.languages)
        self.assertFalse(query.specific)

    def test_invalid_language_code(self):
        language = 'not_a_language'
        query_text = 'the query'
        full_query = ':' + language + ' ' + query_text
        query = RawTextQuery(full_query, [])
        query.parse_query()

        self.assertEquals(query.getFullQuery(), full_query)
        self.assertEquals(len(query.query_parts), 1)
        self.assertEquals(len(query.languages), 0)
        self.assertFalse(query.specific)
