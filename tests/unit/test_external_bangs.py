from searx.external_bang import get_node, resolve_bang_definition, get_bang_url, get_bang_definition_and_autocomplete
from searx.search import SearchQuery, EngineRef
from searx.testing import SearxTestCase


TEST_DB = {
    'trie': {
        'exam': {
            'ple': '//example.com/' + chr(2) + chr(1) + '0',
            '*': '//wikipedia.org/wiki/' + chr(2) + chr(1) + '0',
        },
        'sea': {
            '*': 'sea' + chr(2) + chr(1) + '0',
            'rch': {
                '*': 'search' + chr(2) + chr(1) + '0',
                'ing': 'searching' + chr(2) + chr(1) + '0',
            },
            's': {
                'on': 'season' + chr(2) + chr(1) + '0',
                'capes': 'seascape' + chr(2) + chr(1) + '0',
            }
        },
        'error': ['error in external_bangs.json']
    }
}


class TestGetNode(SearxTestCase):

    DB = {
        'trie': {
            'exam': {
                'ple': 'test',
                '*': 'not used',
            }
        }
    }

    def test_found(self):
        node, before, after = get_node(TestGetNode.DB, 'example')

        self.assertEqual(node, 'test')
        self.assertEqual(before, 'example')
        self.assertEqual(after, '')

    def test_get_partial(self):
        node, before, after = get_node(TestGetNode.DB, 'examp')
        self.assertEqual(node, TestGetNode.DB['trie']['exam'])
        self.assertEqual(before, 'exam')
        self.assertEqual(after, 'p')

    def test_not_found(self):
        node, before, after = get_node(TestGetNode.DB, 'examples')
        self.assertEqual(node, 'test')
        self.assertEqual(before, 'example')
        self.assertEqual(after, 's')


class TestResolveBangDefinition(SearxTestCase):

    def test_https(self):
        url, rank = resolve_bang_definition('//example.com/' + chr(2) + chr(1) + '42', 'query')
        self.assertEqual(url, 'https://example.com/query')
        self.assertEqual(rank, 42)

    def test_http(self):
        url, rank = resolve_bang_definition('http://example.com/' + chr(2) + chr(1) + '0', 'text')
        self.assertEqual(url, 'http://example.com/text')
        self.assertEqual(rank, 0)


class TestGetBangDefinitionAndAutocomplete(SearxTestCase):

    def test_found(self):
        bang_definition, new_autocomplete = get_bang_definition_and_autocomplete('exam', external_bangs_db=TEST_DB)
        self.assertEqual(bang_definition, TEST_DB['trie']['exam']['*'])
        self.assertEqual(new_autocomplete, ['example'])

    def test_found_optimized(self):
        bang_definition, new_autocomplete = get_bang_definition_and_autocomplete('example', external_bangs_db=TEST_DB)
        self.assertEqual(bang_definition, TEST_DB['trie']['exam']['ple'])
        self.assertEqual(new_autocomplete, [])

    def test_partial(self):
        bang_definition, new_autocomplete = get_bang_definition_and_autocomplete('examp', external_bangs_db=TEST_DB)
        self.assertEqual(bang_definition, None)
        self.assertEqual(new_autocomplete, ['example'])

    def test_partial2(self):
        bang_definition, new_autocomplete = get_bang_definition_and_autocomplete('sea', external_bangs_db=TEST_DB)
        self.assertEqual(bang_definition, TEST_DB['trie']['sea']['*'])
        self.assertEqual(new_autocomplete, ['search', 'searching', 'seascapes', 'season'])

    def test_error(self):
        bang_definition, new_autocomplete = get_bang_definition_and_autocomplete('error', external_bangs_db=TEST_DB)
        self.assertEqual(bang_definition, None)
        self.assertEqual(new_autocomplete, [])

    def test_actual_data(self):
        bang_definition, new_autocomplete = get_bang_definition_and_autocomplete('duckduckgo')
        self.assertTrue(bang_definition.startswith('//duckduckgo.com/?q='))
        self.assertEqual(new_autocomplete, [])


class TestExternalBangJson(SearxTestCase):

    def test_no_external_bang_query(self):
        result = get_bang_url(SearchQuery('test', engineref_list=[EngineRef('wikipedia', 'general')]))
        self.assertEqual(result, None)

    def test_get_bang_url(self):
        url = get_bang_url(SearchQuery('test', engineref_list=[], external_bang='example'), external_bangs_db=TEST_DB)
        self.assertEqual(url, 'https://example.com/test')

    def test_actual_data(self):
        google_url = get_bang_url(SearchQuery('test', engineref_list=[], external_bang='g'))
        self.assertEqual(google_url, 'https://www.google.com/search?q=test')
