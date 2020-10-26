from searx.query import RawTextQuery
from searx.testing import SearxTestCase


class TestQuery(SearxTestCase):

    def test_simple_query(self):
        query_text = 'the query'
        query = RawTextQuery(query_text, [])

        self.assertEqual(query.getFullQuery(), query_text)
        self.assertEqual(len(query.query_parts), 0)
        self.assertEqual(len(query.user_query_parts), 2)
        self.assertEqual(len(query.languages), 0)
        self.assertFalse(query.specific)

    def test_language_code(self):
        language = 'es-ES'
        query_text = 'the query'
        full_query = ':' + language + ' ' + query_text
        query = RawTextQuery(full_query, [])

        self.assertEqual(query.getFullQuery(), full_query)
        self.assertEqual(len(query.query_parts), 1)
        self.assertEqual(len(query.languages), 1)
        self.assertIn(language, query.languages)
        self.assertFalse(query.specific)

    def test_language_name(self):
        language = 'english'
        query_text = 'the query'
        full_query = ':' + language + ' ' + query_text
        query = RawTextQuery(full_query, [])

        self.assertEqual(query.getFullQuery(), full_query)
        self.assertEqual(len(query.query_parts), 1)
        self.assertIn('en', query.languages)
        self.assertFalse(query.specific)

    def test_unlisted_language_code(self):
        language = 'all'
        query_text = 'the query'
        full_query = ':' + language + ' ' + query_text
        query = RawTextQuery(full_query, [])

        self.assertEqual(query.getFullQuery(), full_query)
        self.assertEqual(len(query.query_parts), 1)
        self.assertIn('all', query.languages)
        self.assertFalse(query.specific)

    def test_invalid_language_code(self):
        language = 'not_a_language'
        query_text = 'the query'
        full_query = ':' + language + ' ' + query_text
        query = RawTextQuery(full_query, [])

        self.assertEqual(query.getFullQuery(), full_query)
        self.assertEqual(len(query.query_parts), 0)
        self.assertEqual(len(query.languages), 0)
        self.assertFalse(query.specific)

    def test_timeout_below100(self):
        query_text = '<3 the query'
        query = RawTextQuery(query_text, [])

        self.assertEqual(query.getFullQuery(), query_text)
        self.assertEqual(len(query.query_parts), 1)
        self.assertEqual(query.timeout_limit, 3)
        self.assertFalse(query.specific)

    def test_timeout_above100(self):
        query_text = '<350 the query'
        query = RawTextQuery(query_text, [])

        self.assertEqual(query.getFullQuery(), query_text)
        self.assertEqual(len(query.query_parts), 1)
        self.assertEqual(query.timeout_limit, 0.35)
        self.assertFalse(query.specific)

    def test_timeout_above1000(self):
        query_text = '<3500 the query'
        query = RawTextQuery(query_text, [])

        self.assertEqual(query.getFullQuery(), query_text)
        self.assertEqual(len(query.query_parts), 1)
        self.assertEqual(query.timeout_limit, 3.5)
        self.assertFalse(query.specific)

    def test_timeout_invalid(self):
        # invalid number: it is not bang but it is part of the query
        query_text = '<xxx the query'
        query = RawTextQuery(query_text, [])

        self.assertEqual(query.getFullQuery(), query_text)
        self.assertEqual(len(query.query_parts), 0)
        self.assertEqual(query.getQuery(), query_text)
        self.assertEqual(query.timeout_limit, None)
        self.assertFalse(query.specific)
