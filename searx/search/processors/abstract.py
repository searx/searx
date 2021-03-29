# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import abstractmethod, ABC
from searx import logger


logger = logger.getChild('searx.search.processor')


class EngineProcessor(ABC):

    def __init__(self, engine, engine_name):
        self.engine = engine
        self.engine_name = engine_name

    def get_params(self, search_query, engine_category):
        # if paging is not supported, skip
        if search_query.pageno > 1 and not self.engine.paging:
            return None

        # if time_range is not supported, skip
        if search_query.time_range and not self.engine.time_range_support:
            return None

        params = {}
        params['category'] = engine_category
        params['pageno'] = search_query.pageno
        params['safesearch'] = search_query.safesearch
        params['time_range'] = search_query.time_range
        params['engine_data'] = search_query.engine_data.get(self.engine_name, {})

        if hasattr(self.engine, 'language') and self.engine.language:
            params['language'] = self.engine.language
        else:
            params['language'] = search_query.lang
        return params

    @abstractmethod
    def search(self, query, params, result_container, start_time, timeout_limit):
        pass

    def get_tests(self):
        tests = getattr(self.engine, 'tests', None)
        if tests is None:
            tests = getattr(self.engine, 'additional_tests', {})
            tests.update(self.get_default_tests())
            return tests
        else:
            return tests

    def get_default_tests(self):
        return {}
