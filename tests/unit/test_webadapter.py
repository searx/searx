# -*- coding: utf-8 -*-

from searx.testing import SearxTestCase
from searx.preferences import Preferences
from searx.engines import engines

import searx.search
from searx.search import EngineRef
from searx.webadapter import validate_engineref_list


PRIVATE_ENGINE_NAME = 'general private offline'
TEST_ENGINES = [
    {
        'name': PRIVATE_ENGINE_NAME,
        'engine': 'dummy-offline',
        'categories': 'general',
        'shortcut': 'do',
        'timeout': 3.0,
        'offline': True,
        'tokens': ['my-token'],
    },
]
SEARCHQUERY = [EngineRef(PRIVATE_ENGINE_NAME, 'general')]


class ValidateQueryCase(SearxTestCase):

    @classmethod
    def setUpClass(cls):
        searx.engines.initialize_engines(TEST_ENGINES)

    def test_query_private_engine_without_token(self):
        preferences = Preferences(['oscar'], ['general'], engines, [])
        valid, unknown, invalid_token = validate_engineref_list(SEARCHQUERY, preferences)
        self.assertEqual(len(valid), 0)
        self.assertEqual(len(unknown), 0)
        self.assertEqual(len(invalid_token), 1)

    def test_query_private_engine_with_incorrect_token(self):
        preferences_with_tokens = Preferences(['oscar'], ['general'], engines, [])
        preferences_with_tokens.parse_dict({'tokens': 'bad-token'})
        valid, unknown, invalid_token = validate_engineref_list(SEARCHQUERY, preferences_with_tokens)
        self.assertEqual(len(valid), 0)
        self.assertEqual(len(unknown), 0)
        self.assertEqual(len(invalid_token), 1)

    def test_query_private_engine_with_correct_token(self):
        preferences_with_tokens = Preferences(['oscar'], ['general'], engines, [])
        preferences_with_tokens.parse_dict({'tokens': 'my-token'})
        valid, unknown, invalid_token = validate_engineref_list(SEARCHQUERY, preferences_with_tokens)
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(unknown), 0)
        self.assertEqual(len(invalid_token), 0)
