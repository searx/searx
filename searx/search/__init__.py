'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2013- by Adam Tauber, <asciimoo@gmail.com>
'''

import typing
import gc
import threading
from time import time
from uuid import uuid4
from _thread import start_new_thread

from searx import settings
from searx.answerers import ask
from searx.external_bang import get_bang_url
from searx.results import ResultContainer
from searx import logger
from searx.plugins import plugins
from searx.search.models import EngineRef, SearchQuery
from searx.search.processors import processors, initialize as initialize_processors
from searx.search.checker import initialize as initialize_checker


logger = logger.getChild('search')

max_request_timeout = settings.get('outgoing', {}).get('max_request_timeout' or None)
if max_request_timeout is None:
    logger.info('max_request_timeout={0}'.format(max_request_timeout))
else:
    if isinstance(max_request_timeout, float):
        logger.info('max_request_timeout={0} second(s)'.format(max_request_timeout))
    else:
        logger.critical('outgoing.max_request_timeout if defined has to be float')
        import sys
        sys.exit(1)


def initialize(settings_engines=None, enable_checker=False):
    settings_engines = settings_engines or settings['engines']
    initialize_processors(settings_engines)
    if enable_checker:
        initialize_checker()


class Search:
    """Search information container"""

    __slots__ = "search_query", "result_container", "start_time", "actual_timeout"

    def __init__(self, search_query):
        # init vars
        super().__init__()
        self.search_query = search_query
        self.result_container = ResultContainer()
        self.start_time = None
        self.actual_timeout = None

    def search_external_bang(self):
        """
        Check if there is a external bang.
        If yes, update self.result_container and return True
        """
        if self.search_query.external_bang:
            self.result_container.redirect_url = get_bang_url(self.search_query)

            # This means there was a valid bang and the
            # rest of the search does not need to be continued
            if isinstance(self.result_container.redirect_url, str):
                return True
        return False

    def search_answerers(self):
        """
        Check if an answer return a result.
        If yes, update self.result_container and return True
        """
        answerers_results = ask(self.search_query)

        if answerers_results:
            for results in answerers_results:
                self.result_container.extend('answer', results)
            return True
        return False

    # do search-request
    def _get_requests(self):
        # init vars
        requests = []

        # max of all selected engine timeout
        default_timeout = 0

        # start search-reqest for all selected engines
        for engineref in self.search_query.engineref_list:
            processor = processors[engineref.name]

            # set default request parameters
            request_params = processor.get_params(self.search_query, engineref.category)
            if request_params is None:
                continue

            with threading.RLock():
                processor.engine.stats['sent_search_count'] += 1

            # append request to list
            requests.append((engineref.name, self.search_query.query, request_params))

            # update default_timeout
            default_timeout = max(default_timeout, processor.engine.timeout)

        # adjust timeout
        actual_timeout = default_timeout
        query_timeout = self.search_query.timeout_limit

        if max_request_timeout is None and query_timeout is None:
            # No max, no user query: default_timeout
            pass
        elif max_request_timeout is None and query_timeout is not None:
            # No max, but user query: From user query except if above default
            actual_timeout = min(default_timeout, query_timeout)
        elif max_request_timeout is not None and query_timeout is None:
            # Max, no user query: Default except if above max
            actual_timeout = min(default_timeout, max_request_timeout)
        elif max_request_timeout is not None and query_timeout is not None:
            # Max & user query: From user query except if above max
            actual_timeout = min(query_timeout, max_request_timeout)

        logger.debug("actual_timeout={0} (default_timeout={1}, ?timeout_limit={2}, max_request_timeout={3})"
                     .format(actual_timeout, default_timeout, query_timeout, max_request_timeout))

        return requests, actual_timeout

    def search_multiple_requests(self, requests):
        search_id = uuid4().__str__()

        for engine_name, query, request_params in requests:
            th = threading.Thread(
                target=processors[engine_name].search,
                args=(query, request_params, self.result_container, self.start_time, self.actual_timeout),
                name=search_id,
            )
            th._timeout = False
            th._engine_name = engine_name
            th.start()

        for th in threading.enumerate():
            if th.name == search_id:
                remaining_time = max(0.0, self.actual_timeout - (time() - self.start_time))
                th.join(remaining_time)
                if th.is_alive():
                    th._timeout = True
                    self.result_container.add_unresponsive_engine(th._engine_name, 'timeout')
                    logger.warning('engine timeout: {0}'.format(th._engine_name))

    def search_standard(self):
        """
        Update self.result_container, self.actual_timeout
        """
        requests, self.actual_timeout = self._get_requests()

        # send all search-request
        if requests:
            self.search_multiple_requests(requests)
            start_new_thread(gc.collect, tuple())

        # return results, suggestions, answers and infoboxes
        return True

    # do search-request
    def search(self):
        self.start_time = time()

        if not self.search_external_bang():
            if not self.search_answerers():
                self.search_standard()

        return self.result_container


class SearchWithPlugins(Search):
    """Similar to the Search class but call the plugins."""

    __slots__ = 'ordered_plugin_list', 'request'

    def __init__(self, search_query, ordered_plugin_list, request):
        super().__init__(search_query)
        self.ordered_plugin_list = ordered_plugin_list
        self.request = request

    def search(self):
        if plugins.call(self.ordered_plugin_list, 'pre_search', self.request, self):
            super().search()

        plugins.call(self.ordered_plugin_list, 'post_search', self.request, self)

        results = self.result_container.get_ordered_results()

        for result in results:
            plugins.call(self.ordered_plugin_list, 'on_result', self.request, self, result)

        return self.result_container
