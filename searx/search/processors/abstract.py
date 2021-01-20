# SPDX-License-Identifier: AGPL-3.0-or-later

import threading
from abc import abstractmethod, ABC
from time import time

from searx import logger
from searx.engines import settings


logger = logger.getChild('searx.search.processor')


class EngineProcessor(ABC):

    def __init__(self, engine, engine_name):
        self.engine = engine
        self.engine_name = engine_name
        self.suspend_end_time = 0
        self.continuous_errors = 0

    def suspend(self, suspended_time):
        with threading.RLock():
            # update continuous_errors / suspend_end_time
            self.continuous_errors += 1
            if suspended_time is None:
                suspended_time = min(settings['search']['max_ban_time_on_fail'],
                                     self.continuous_errors * settings['search']['ban_time_on_fail'])
            self.suspend_end_time = time() + suspended_time
            logger.debug('Suspend engine for %i seconds', suspended_time)

    def sucessful_request(self):
        with threading.RLock():
            # reset the suspend variables
            self.continuous_errors = 0
            self.suspend_end_time = 0

    def get_params(self, search_query, engine_category):
        # skip suspended engines
        if self.suspend_end_time >= time():
            logger.debug('Engine currently suspended: %s', self.engine_name)
            return None

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
