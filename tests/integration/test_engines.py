from os import path, listdir 
from searx import settings, engines
from searx.search import SearchQuery, Search, EngineRef
from searx.search import initialize
from searx.testing import SearxTestCase
from typing import Tuple
import sys
import logging
import requests 
import searx

logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

SAFESEARCH = 0
PAGENO = 1

SKIP_ENGINES = set([
    'command',
    'elasticsearch',
    'flickr',
    'json_engine',
    'meilisearch',
    'mongodb',
    'mysql_server',
    'omnom',
    'postgresql',
    'prowlarr',
    'recoll',
    'redis_server',
    'solr',
    'spotify',
    'sqlite',
    'xpath',
    'xpath_flex',
    'yggtorrent',
    'youtube_api',
    ])

TEST_ENGINES = set([
    'bing',
    'duckduckgo',
    'google',
    'bandcamp',
    'yahoo',
    'startpage',
    ])

class TestEnginesSingleSearch(SearxTestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine_names = []
        engine_data = []

        def add_engine(file):
            engine_name = file.replace('.py', '')
            if engine_name in SKIP_ENGINES:
                return
            engine_name_normalized = engine_name.replace('_', '-') + '-test'
            engine_data.append({
                'engine': engine_name, 
                'name': engine_name_normalized,
                'categories': 'general',
                'shortcut': engine_name,
                'timeout': 3.0,
                'tokens': []
                })
            cls.engine_names.append(engine_name_normalized)

        for e in TEST_ENGINES:
            add_engine(e)

        initialize(engine_data)

    @classmethod
    def tearDownClass(cls):
        settings['outgoing']['using_tor_proxy'] = False
        settings['outgoing']['extra_proxy_timeout'] = 0

    def test_search_engines(self):
        def test_single_result(engine_name: str) -> Tuple[str, Exception, int]:
            logger.debug('---------------------------')
            logger.info(f'Testing Engine: {engine_name}')
            try:
                search_query = SearchQuery('test', [EngineRef(engine_name, 'general')],
                                   'en-US', SAFESEARCH, PAGENO, None, None)
                search = Search(search_query)
                info = search.search()
                return (engine_name, None, info.results_number())
            except Exception as e:
                return (engine_name, e, 0)
            finally:
                logger.debug('---------------------------')

        results = [test_single_result(engine_name) for engine_name in self.engine_names]
        engines_passed = []
        engines_exception = []
        engines_no_results = []
        for r in results:
            if r[1] is not None:
                engines_exception.append(r)
            elif r[2] <= 0:
                engines_no_results.append(r)
            else:
                engines_passed.append(r)

        def log_results(lst, name):
            logger.info(f'{name}: {len(lst)}')
            for e in lst:
                logger.info(f'{name}: {e[0]}')


        log_results(engines_passed, 'engines_passed')
        log_results(engines_exception, 'engines_exception')
        log_results(engines_no_results, 'engines_no_results')

        self.assertEqual(len(engines_exception), 0)
        self.assertEqual(len(engines_no_results), 0)

