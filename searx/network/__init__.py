# SPDX-License-Identifier: AGPL-3.0-or-later

import asyncio
import threading
import concurrent.futures
from time import time

import httpx
import h2.exceptions

from .network import get_network, initialize, check_network_configuration
from .client import get_loop
from .raise_for_httperror import raise_for_httperror

# queue.SimpleQueue: Support Python 3.6
try:
    from queue import SimpleQueue
except ImportError:
    from queue import Empty
    from collections import deque

    class SimpleQueue:
        """Minimal backport of queue.SimpleQueue"""

        def __init__(self):
            self._queue = deque()
            self._count = threading.Semaphore(0)

        def put(self, item):
            self._queue.append(item)
            self._count.release()

        def get(self):
            if not self._count.acquire(True):
                raise Empty
            return self._queue.popleft()


THREADLOCAL = threading.local()


def reset_time_for_thread():
    THREADLOCAL.total_time = 0


def get_time_for_thread():
    return THREADLOCAL.total_time


def set_timeout_for_thread(timeout, start_time=None):
    THREADLOCAL.timeout = timeout
    THREADLOCAL.start_time = start_time


def set_context_network_name(network_name):
    THREADLOCAL.network = get_network(network_name)


def get_context_network():
    try:
        return THREADLOCAL.network
    except AttributeError:
        return get_network()


def request(method, url, **kwargs):
    """same as requests/requests/api.py request(...)"""
    time_before_request = time()

    # timeout (httpx)
    if 'timeout' in kwargs:
        timeout = kwargs['timeout']
    else:
        timeout = getattr(THREADLOCAL, 'timeout', None)
        if timeout is not None:
            kwargs['timeout'] = timeout

    # 2 minutes timeout for the requests without timeout
    timeout = timeout or 120

    # ajdust actual timeout
    timeout += 0.2  # overhead
    start_time = getattr(THREADLOCAL, 'start_time', time_before_request)
    if start_time:
        timeout -= time() - start_time

    # raise_for_error
    check_for_httperror = True
    if 'raise_for_httperror' in kwargs:
        check_for_httperror = kwargs['raise_for_httperror']
        del kwargs['raise_for_httperror']

    # requests compatibility
    if isinstance(url, bytes):
        url = url.decode()

    # network
    network = get_context_network()

    # do request
    future = asyncio.run_coroutine_threadsafe(network.request(method, url, **kwargs), get_loop())
    try:
        response = future.result(timeout)
    except concurrent.futures.TimeoutError as e:
        raise httpx.TimeoutException('Timeout', request=None) from e

    # requests compatibility
    # see also https://www.python-httpx.org/compatibility/#checking-for-4xx5xx-responses
    response.ok = not response.is_error

    # update total_time.
    # See get_time_for_thread() and reset_time_for_thread()
    if hasattr(THREADLOCAL, 'total_time'):
        time_after_request = time()
        THREADLOCAL.total_time += time_after_request - time_before_request

    # raise an exception
    if check_for_httperror:
        raise_for_httperror(response)

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


async def stream_chunk_to_queue(network, q, method, url, **kwargs):
    try:
        async with await network.stream(method, url, **kwargs) as response:
            q.put(response)
            async for chunk in response.aiter_bytes(65536):
                if len(chunk) > 0:
                    q.put(chunk)
    except (httpx.HTTPError, OSError, h2.exceptions.ProtocolError) as e:
        q.put(e)
    finally:
        q.put(None)


def stream(method, url, **kwargs):
    """Replace httpx.stream.

    Usage:
    stream = poolrequests.stream(...)
    response = next(stream)
    for chunk in stream:
        ...

    httpx.Client.stream requires to write the httpx.HTTPTransport version of the
    the httpx.AsyncHTTPTransport declared above.
    """
    q = SimpleQueue()
    future = asyncio.run_coroutine_threadsafe(stream_chunk_to_queue(get_network(), q, method, url, **kwargs),
                                              get_loop())
    chunk_or_exception = q.get()
    while chunk_or_exception is not None:
        if isinstance(chunk_or_exception, Exception):
            raise chunk_or_exception
        yield chunk_or_exception
        chunk_or_exception = q.get()
    return future.result()
