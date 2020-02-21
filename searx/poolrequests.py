from time import time
from itertools import cycle
import threading
import concurrent.futures
import asyncio
import logging

import uvloop
import httpcore
import httpx

from searx import settings
from searx import logger

logger = logger.getChild('poolrequests')


try:
    import ssl
    if ssl.OPENSSL_VERSION_INFO[0:3] < (1, 0, 2):
        # https://github.com/certifi/python-certifi#1024-bit-root-certificates
        logger.critical('You are using an old openssl version({0}), please upgrade above 1.0.2!'
                        .format(ssl.OPENSSL_VERSION))
        sys.exit(1)
except ImportError:
    ssl = None
if not getattr(ssl, "HAS_SNI", False):
    try:
        import OpenSSL  # pylint: disable=unused-import
    except ImportError:
        logger.critical("ssl doesn't support SNI and the pyopenssl module is not installed.\n"
                        "Some HTTPS connections will fail")
        sys.exit(1)


LOOP = None
CLIENTS = dict()
THREADLOCAL = threading.local()
POOL_CONNECTIONS = settings['outgoing'].get('pool_connections', 100)  # Magic number kept from previous code
POOL_MAXSIZE = settings['outgoing'].get('pool_maxsize', 10)  # Picked from constructor

if settings['outgoing'].get('source_ips'):
    LOCAL_ADDRESS_CYCLE = cycle(settings['outgoing'].get('source_ips'))
else:
    LOCAL_ADDRESS_CYCLE = cycle((None, ))


def set_timeout_for_thread(timeout, start_time=None):
    THREADLOCAL.timeout = timeout
    THREADLOCAL.start_time = start_time


def reset_time_for_thread():
    THREADLOCAL.total_time = 0


def get_time_for_thread():
    return THREADLOCAL.total_time


async def get_client(verify, proxies):
    global CLIENTS, POOL_CONNECTIONS, POOL_MAXSIZE

    if proxies is None:
        local_address = next(LOCAL_ADDRESS_CYCLE)
        key = (verify, local_address, None)
    else:
        local_address = None
        key = (verify, local_address, str(proxies))

    if key not in CLIENTS:
        ssl_context = httpx.create_ssl_context() if verify else None
        transport = httpcore.AsyncConnectionPool(ssl_context=ssl_context,
                                                 max_connections=POOL_CONNECTIONS,
                                                 max_keepalive_connections=POOL_MAXSIZE,
                                                 local_address=local_address,
                                                 http2=True)
        client = httpx.AsyncClient(transport=transport, proxies=proxies)
        CLIENTS[key] = client
    else:
        client = CLIENTS[key]
    return client


async def send_request(method, url, kwargs):
    if isinstance(url, bytes):
        url = url.decode()

    client = await get_client(kwargs.get('verify', True), kwargs.get('proxies', None))
    if 'verify' in kwargs:
        del kwargs['verify']
    if 'proxies' in kwargs:
        del kwargs['proxies']
    if 'stream' in kwargs:
        del kwargs['stream']
        raise NotImplementedError('stream not supported')

    response = await client.request(method.upper(), url, **kwargs)

    # requests compatibility
    try:
        response.raise_for_status()
        response.ok = True
    except httpx.HTTPError:
        response.ok = False

    return response


def request(method, url, **kwargs):
    global LOOP

    """same as requests/requests/api.py request(...)"""
    time_before_request = time()

    # proxies
    if kwargs.get('proxies') is None:
        kwargs['proxies'] = settings['outgoing'].get('proxies')

    # timeout
    if 'timeout' in kwargs:
        timeout = kwargs['timeout']
    else:
        timeout = getattr(THREADLOCAL, 'timeout', None)
        if timeout is not None:
            kwargs['timeout'] = timeout

    # do request
    future = asyncio.run_coroutine_threadsafe(send_request(method, url, kwargs), LOOP)
    response = future.result()

    time_after_request = time()

    # is there a timeout for this engine ?
    if timeout is not None:
        timeout_overhead = 0.2  # seconds
        # start_time = when the user request started
        start_time = getattr(THREADLOCAL, 'start_time', time_before_request)
        search_duration = time_after_request - start_time
        if search_duration > timeout + timeout_overhead:
            # FIXME: should not be request=None
            raise httpx.ReadTimeout(message='Timeout', request=None)

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


def init():
    # log
    for logger_name in ('hpack.hpack', 'hpack.table'):
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # loop
    def loop_thread():
        global LOOP
        LOOP = uvloop.new_event_loop()
        LOOP.run_forever()

    th = threading.Thread(
        target=loop_thread,
        name='asyncio_loop',
        daemon=True,
    )
    th.start()

init()
