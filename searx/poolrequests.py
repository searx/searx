import requests

from itertools import cycle
from threading import RLock, local
from searx import settings
from time import time


class HTTPAdapterWithConnParams(requests.adapters.HTTPAdapter):

    def __init__(self, pool_connections=requests.adapters.DEFAULT_POOLSIZE,
                 pool_maxsize=requests.adapters.DEFAULT_POOLSIZE,
                 max_retries=requests.adapters.DEFAULT_RETRIES,
                 pool_block=requests.adapters.DEFAULT_POOLBLOCK,
                 **conn_params):
        if max_retries == requests.adapters.DEFAULT_RETRIES:
            self.max_retries = requests.adapters.Retry(0, read=False)
        else:
            self.max_retries = requests.adapters.Retry.from_int(max_retries)
        self.config = {}
        self.proxy_manager = {}

        super(requests.adapters.HTTPAdapter, self).__init__()

        self._pool_connections = pool_connections
        self._pool_maxsize = pool_maxsize
        self._pool_block = pool_block
        self._conn_params = conn_params

        self.init_poolmanager(pool_connections, pool_maxsize, block=pool_block, **conn_params)

    def __setstate__(self, state):
        # Can't handle by adding 'proxy_manager' to self.__attrs__ because
        # because self.poolmanager uses a lambda function, which isn't pickleable.
        self.proxy_manager = {}
        self.config = {}

        for attr, value in state.items():
            setattr(self, attr, value)

        self.init_poolmanager(self._pool_connections, self._pool_maxsize,
                              block=self._pool_block, **self._conn_params)


threadLocal = local()
connect = settings['outgoing'].get('pool_connections', 100)  # Magic number kept from previous code
maxsize = settings['outgoing'].get('pool_maxsize', requests.adapters.DEFAULT_POOLSIZE)  # Picked from constructor
if settings['outgoing'].get('source_ips'):
    http_adapters = cycle(HTTPAdapterWithConnParams(pool_connections=connect, pool_maxsize=maxsize,
                                                    source_address=(source_ip, 0))
                          for source_ip in settings['outgoing']['source_ips'])
    https_adapters = cycle(HTTPAdapterWithConnParams(pool_connections=connect, pool_maxsize=maxsize,
                                                     source_address=(source_ip, 0))
                           for source_ip in settings['outgoing']['source_ips'])
else:
    http_adapters = cycle((HTTPAdapterWithConnParams(pool_connections=connect, pool_maxsize=maxsize), ))
    https_adapters = cycle((HTTPAdapterWithConnParams(pool_connections=connect, pool_maxsize=maxsize), ))


class SessionSinglePool(requests.Session):

    def __init__(self):
        super(SessionSinglePool, self).__init__()

        # reuse the same adapters
        with RLock():
            self.adapters.clear()
            self.mount('https://', next(https_adapters))
            self.mount('http://', next(http_adapters))

    def close(self):
        """Call super, but clear adapters since there are managed globaly"""
        self.adapters.clear()
        super(SessionSinglePool, self).close()


def set_timeout_for_thread(timeout, start_time=None):
    threadLocal.timeout = timeout
    threadLocal.start_time = start_time


def reset_time_for_thread():
    threadLocal.total_time = 0


def get_time_for_thread():
    return threadLocal.total_time


def request(method, url, **kwargs):
    """same as requests/requests/api.py request(...)"""
    time_before_request = time()

    # session start
    session = SessionSinglePool()

    # proxies
    if kwargs.get('proxies') is None:
        kwargs['proxies'] = settings['outgoing'].get('proxies')

    # timeout
    if 'timeout' in kwargs:
        timeout = kwargs['timeout']
    else:
        timeout = getattr(threadLocal, 'timeout', None)
        if timeout is not None:
            kwargs['timeout'] = timeout

    # do request
    response = session.request(method=method, url=url, **kwargs)

    time_after_request = time()

    # is there a timeout for this engine ?
    if timeout is not None:
        timeout_overhead = 0.2  # seconds
        # start_time = when the user request started
        start_time = getattr(threadLocal, 'start_time', time_before_request)
        search_duration = time_after_request - start_time
        if search_duration > timeout + timeout_overhead:
            raise requests.exceptions.Timeout(response=response)

    # session end
    session.close()

    if hasattr(threadLocal, 'total_time'):
        threadLocal.total_time += time_after_request - time_before_request

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
