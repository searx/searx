import threading
import requests.exceptions
import searx.poolrequests as requests_lib
from time import time
from searx import logger

logger = logger.getChild('engine')


def send_http_request(engine, request_params, timeout_limit):
    # for page_load_time stats
    time_before_request = time()

    # create dictionary which contain all
    # informations about the request
    request_args = dict(
        headers=request_params['headers'],
        cookies=request_params['cookies'],
        timeout=timeout_limit,
        verify=request_params['verify']
    )

    # specific type of request (GET or POST)
    if request_params['method'] == 'GET':
        req = requests_lib.get
    else:
        req = requests_lib.post
        request_args['data'] = request_params['data']

    # send the request
    response = req(request_params['url'], **request_args)

    # is there a timeout (no parsing in this case)
    timeout_overhead = 0.2  # seconds
    search_duration = time() - request_params['started']
    if search_duration > timeout_limit + timeout_overhead:
        raise requests.exceptions.Timeout(response=response)

    with threading.RLock():
        # no error : reset the suspend variables
        engine.continuous_errors = 0
        engine.suspend_end_time = 0
        # update stats with current page-load-time
        # only the HTTP request
        engine.stats['page_load_time'] += time() - time_before_request
        engine.stats['page_load_count'] += 1

    # everything is ok : return the response
    return response


def get_default_search(engine):

    def search(query, request_params, timeout_limit):
        # update request parameters dependent on
        # search-engine (contained in engines folder)
        engine.request(query, request_params)

        # check if there is a HTTP request
        if request_params['url'] is None:
            return []

        if not request_params['url']:
            return []

        # send request
        response = send_http_request(engine, request_params, timeout_limit)

        # parse the response
        response.search_params = request_params
        return engine.response(response)

    return search


def get_default_can_accept_search_query(engine):

    def can_accept_search_query(search_query):
        # if paging is not supported, skip
        if search_query.pageno > 1 and not engine.paging:
            return False

        # if search-language is set and engine does not
        # provide language-support, skip
        if search_query.lang != 'all' and not engine.language_support:
            return False

        # if time_range is not supported, skip
        if search_query.time_range and not engine.time_range_support:
            return False

        return True

    return can_accept_search_query
