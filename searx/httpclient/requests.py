# -*- coding: utf-8 -*-
import threading
import time
from searx.httpclient.sessions import Session
from searx import settings, logger

THREADLOCAL = threading.local()

max_host_connections = settings['outgoing'].get('pool_maxsize', 10)
max_total_connections = max_host_connections * settings['outgoing'].get('pool_connections', 100)
SESSION = Session(share_cookies=False,
                  http2=True,
                  max_total_connections=max_total_connections,
                  max_host_connections=max_host_connections)


def set_timeout_for_thread(timeout, start_time=None):
    THREADLOCAL.timeout = timeout
    THREADLOCAL.start_time = start_time


def reset_time_for_thread():
    THREADLOCAL.total_time = 0


def get_time_for_thread():
    return THREADLOCAL.total_time


def request(method, url, **kwargs):
    """same as requests/requests/api.py request(...)"""
    time_before_request = time.time()

    # proxies
    kwargs['proxies'] = settings['outgoing'].get('proxies') or None

    # timeout
    if 'timeout' in kwargs:
        timeout = kwargs['timeout']
    else:
        timeout = getattr(THREADLOCAL, 'timeout', None)
        if timeout is not None:
            kwargs['timeout'] = timeout

    # do request
    response = SESSION.request(method, url, **kwargs)

    time_after_request = time.time()

    # is there a timeout for this engine ?
    if timeout is not None:
        timeout_overhead = 0.2  # seconds
        # start_time = when the user request started
        start_time = getattr(THREADLOCAL, 'start_time', time_before_request)
        search_duration = time_after_request - start_time
        if search_duration > timeout + timeout_overhead:
            raise TimeoutError(response=response)

    if hasattr(THREADLOCAL, 'total_time'):
        THREADLOCAL.total_time += time_after_request - time_before_request

    return response


def get(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('get', url, **kwargs)


def options(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('options', url, **kwargs)


def head(url, **kwargs):
    kwargs.setdefault('allow_redirects', False)
    return request('head', url, **kwargs)


def post(url, data=None, **kwargs):
    return request('post', url, data=data, **kwargs)


def put(url, data=None, **kwargs):
    return request('put', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    return request('patch', url, data=data, **kwargs)


def delete(url, **kwargs):
    return request('delete', url, **kwargs)
