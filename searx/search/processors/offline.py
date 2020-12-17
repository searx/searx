# SPDX-License-Identifier: AGPL-3.0-or-later

import threading
from time import time
from searx import logger
from searx.metrology.error_recorder import record_exception, record_error
from searx.search.processors.abstract import EngineProcessor


logger = logger.getChild('search.processor.offline')


class OfflineProcessor(EngineProcessor):

    engine_type = 'offline'

    def _record_stats_on_error(self, result_container, start_time):
        engine_time = time() - start_time
        result_container.add_timing(self.engine_name, engine_time, engine_time)

        with threading.RLock():
            self.engine.stats['errors'] += 1

    def _search_basic(self, query, params):
        return self.engine.search(query, params)

    def search(self, query, params, result_container, start_time, timeout_limit):
        try:
            search_results = self._search_basic(query, params)

            if search_results:
                result_container.extend(self.engine_name, search_results)

                engine_time = time() - start_time
                result_container.add_timing(self.engine_name, engine_time, engine_time)
                with threading.RLock():
                    self.engine.stats['engine_time'] += engine_time
                    self.engine.stats['engine_time_count'] += 1

        except ValueError as e:
            record_exception(self.engine_name, e)
            self._record_stats_on_error(result_container, start_time)
            logger.exception('engine {0} : invalid input : {1}'.format(self.engine_name, e))
        except Exception as e:
            record_exception(self.engine_name, e)
            self._record_stats_on_error(result_container, start_time)
            result_container.add_unresponsive_engine(self.engine_name, 'unexpected crash', str(e))
            logger.exception('engine {0} : exception : {1}'.format(self.engine_name, e))
        else:
            if getattr(threading.current_thread(), '_timeout', False):
                record_error(self.engine_name, 'Timeout')
