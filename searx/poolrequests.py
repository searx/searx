import atexit
import sys
import threading
import asyncio
import logging
from time import time
from itertools import cycle
from queue import SimpleQueue

import uvloop
import httpcore
import httpx
import h2.exceptions
from httpx_socks import AsyncProxyTransport
from python_socks import parse_proxy_url
import python_socks._errors

from searx import settings
from searx import logger
from searx.raise_for_httperror import raise_for_httperror


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
SYNC_CLIENT = None
THREADLOCAL = threading.local()
LIMITS = httpx.Limits(
    # Magic number kept from previous code
    max_connections=settings['outgoing'].get('pool_connections', 100),
    # Picked from constructor
    max_keepalive_connections=settings['outgoing'].get('pool_maxsize', 10)
)
# default parameters for AsyncHTTPTransport
# see https://github.com/encode/httpx/blob/e05a5372eb6172287458b37447c30f650047e1b8/httpx/_transports/default.py#L108-L121   # noqa
TRANSPORT_KWARGS = {
    'http2': settings['outgoing'].get('http2', False),
    'retries': 0,
    'trust_env': False,
    'backend': 'asyncio'
}
# requests compatibility when reading proxy settings from settings.yml
PROXY_PATTERN_MAPPING = {
    'http': 'https://',
    'https:': 'https://'
}


if settings['outgoing'].get('source_ips'):
    LOCAL_ADDRESS_CYCLE = cycle(settings['outgoing'].get('source_ips'))
else:
    LOCAL_ADDRESS_CYCLE = cycle((None, ))


def set_timeout_for_thread(timeout, start_time=None):
    THREADLOCAL.timeout = timeout
    THREADLOCAL.start_time = start_time


def set_enable_http_protocol(enable_http):
    THREADLOCAL.enable_http = enable_http


def get_enable_http_protocol():
    try:
        return THREADLOCAL.enable_http
    except AttributeError:
        return False


def reset_time_for_thread():
    THREADLOCAL.total_time = 0


def get_time_for_thread():
    return THREADLOCAL.total_time


def get_proxy_cycles(proxy_settings):
    if not proxy_settings:
        return None
    # Backwards compatibility for single proxy in settings.yml
    for protocol, proxy in proxy_settings.items():
        if isinstance(proxy, str):
            proxy_settings[protocol] = [proxy]

    for protocol in proxy_settings:
        proxy_settings[protocol] = cycle(proxy_settings[protocol])
    return proxy_settings


GLOBAL_PROXY_CYCLES = get_proxy_cycles(settings['outgoing'].get('proxies'))


def get_proxies(proxy_cycles):
    if proxy_cycles:
        return {protocol: next(proxy_cycle) for protocol, proxy_cycle in proxy_cycles.items()}
    return None


def get_global_proxies():
    return get_proxies(GLOBAL_PROXY_CYCLES)


class AsyncHTTPTransportNoHttp(httpcore.AsyncHTTPTransport):
    """Block HTTP request"""

    async def arequest(self, method, url, headers=None, stream=None, ext=None):
        raise httpcore.UnsupportedProtocol("HTTP protocol is disable")


class AsyncProxyTransportFixed(AsyncProxyTransport):
    """Fix httpx_socks.AsyncProxyTransport

    Map python_socks exceptions to httpcore.ProxyError

    Map socket.gaierror to httpcore.ConnectError
    """

    async def arequest(self, method, url, headers=None, stream=None, ext=None):
        try:
            return await super().arequest(method, url, headers, stream, ext)
        except (python_socks._errors.ProxyConnectionError,
                python_socks._errors.ProxyTimeoutError,
                python_socks._errors.ProxyError) as e:
            raise httpcore.ProxyError(e)
        except OSError as e:
            # socket.gaierror when DNS resolution fails
            raise httpcore.NetworkError(e)


class AsyncHTTPTransportFixed(httpx.AsyncHTTPTransport):
    """Fix httpx.AsyncHTTPTransport

    Map socket.gaierror to httpcore.ConnectError
    """

    async def arequest(self, method, url, headers=None, stream=None, ext=None):
        try:
            return await super().arequest(method, url, headers, stream, ext)
        except OSError as e:
            # socket.gaierror when DNS resolution fails
            raise httpcore.ConnectError(e)


def get_transport_for_socks_proxy(verify, local_address, proxy_url):
    global LOOP, LIMITS, TRANSPORT_KWARGS
    # support socks5h (requests compatibility):
    # https://requests.readthedocs.io/en/master/user/advanced/#socks
    # socks5://   hostname is resolved on client side
    # socks5h://  hostname is resolved on proxy side
    rdns = False
    socks5h = 'socks5h://'
    if proxy_url.startswith(socks5h):
        proxy_url = 'socks5://' + proxy_url[len(socks5h):]
        rdns = True

    proxy_type, proxy_host, proxy_port, proxy_username, proxy_password = parse_proxy_url(proxy_url)

    return AsyncProxyTransportFixed(proxy_type=proxy_type, proxy_host=proxy_host, proxy_port=proxy_port,
                                    username=proxy_username, password=proxy_password,
                                    rdns=rdns,
                                    loop=LOOP,
                                    verify=verify,
                                    local_address=local_address,
                                    max_connections=LIMITS.max_connections,
                                    max_keepalive_connections=LIMITS.max_keepalive_connections,
                                    keepalive_expiry=LIMITS.keepalive_expiry,
                                    **TRANSPORT_KWARGS)


def get_transport(verify, local_address, proxy_url):
    global LIMITS
    return AsyncHTTPTransportFixed(verify=verify,
                                   local_address=local_address,
                                   limits=LIMITS,
                                   proxy=httpx._config.Proxy(proxy_url) if proxy_url else None,
                                   **TRANSPORT_KWARGS)


def iter_proxies(proxies):
    # https://www.python-httpx.org/compatibility/#proxy-keys
    if isinstance(proxies, str):
        yield 'all://', proxies
    elif isinstance(proxies, dict):
        for pattern, proxy_url in proxies.items():
            pattern = PROXY_PATTERN_MAPPING.get(pattern, pattern)
            yield pattern, proxy_url


def new_client(verify, local_address, proxies, max_redirects, enable_http):
    # See https://www.python-httpx.org/advanced/#routing
    mounts = {}
    for pattern, proxy_url in iter_proxies(proxies):
        if not enable_http and (pattern == 'http' or pattern.startswith('http://')):
            continue
        if proxy_url.startswith('socks4://') \
           or proxy_url.startswith('socks5://') \
           or proxy_url.startswith('socks5h://'):
            mounts[pattern] = get_transport_for_socks_proxy(verify, local_address, proxy_url)
        else:
            mounts[pattern] = get_transport(verify, local_address, proxy_url)

    if not enable_http:
        mounts['http://'] = AsyncHTTPTransportNoHttp()

    transport = get_transport(verify, local_address, None)
    return httpx.AsyncClient(transport=transport, mounts=mounts, max_redirects=max_redirects)


async def get_client(verify, local_address, proxies, max_redirects, allow_http):
    global CLIENTS
    key = (verify, local_address, repr(proxies), max_redirects, allow_http)
    if key not in CLIENTS:
        CLIENTS[key] = new_client(verify, local_address, proxies, max_redirects, allow_http)
    return CLIENTS[key]


async def send_request(method, url, enable_http, kwargs):
    if isinstance(url, bytes):
        url = url.decode()

    verify = kwargs.pop('verify', True)
    local_address = next(LOCAL_ADDRESS_CYCLE)
    proxies = kwargs.pop('proxies', None) or get_global_proxies()
    max_redirects = kwargs.pop('max_redirects', 0)

    client = await get_client(verify, local_address, proxies, max_redirects, enable_http)
    response = await client.request(method.upper(), url, **kwargs)

    # requests compatibility
    # see also https://www.python-httpx.org/compatibility/#checking-for-4xx5xx-responses
    response.ok = not response.is_error

    return response


def request(method, url, **kwargs):
    """same as requests/requests/api.py request(...)"""
    time_before_request = time()

    # timeout
    if 'timeout' in kwargs:
        timeout = kwargs['timeout']
    else:
        timeout = getattr(THREADLOCAL, 'timeout', None)
        if timeout is not None:
            kwargs['timeout'] = timeout

    # raise_for_error
    check_for_httperror = True
    if 'raise_for_httperror' in kwargs:
        check_for_httperror = kwargs['raise_for_httperror']
        del kwargs['raise_for_httperror']

    # do request
    future = asyncio.run_coroutine_threadsafe(send_request(method, url, get_enable_http_protocol(), kwargs), LOOP)
    response = future.result()

    time_after_request = time()

    # is there a timeout for this engine ?
    if timeout is not None:
        timeout_overhead = 0.2  # seconds
        # start_time = when the user request started
        start_time = getattr(THREADLOCAL, 'start_time', time_before_request)
        search_duration = time_after_request - start_time
        if search_duration > timeout + timeout_overhead:
            raise httpx.TimeoutException('Timeout', request=response.request)

    if hasattr(THREADLOCAL, 'total_time'):
        THREADLOCAL.total_time += time_after_request - time_before_request

    # raise an exception
    if check_for_httperror:
        raise_for_httperror(response)

    return response


async def stream_chunk_to_queue(method, url, q, **kwargs):
    verify = kwargs.pop('verify', True)
    local_address = next(LOCAL_ADDRESS_CYCLE)
    proxies = kwargs.pop('proxies', None) or get_global_proxies()
    max_redirects = kwargs.pop('max_redirects', 0)
    client = await get_client(verify, local_address, proxies, max_redirects, True)
    try:
        async with client.stream(method, url, **kwargs) as response:
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
    future = asyncio.run_coroutine_threadsafe(stream_chunk_to_queue(method, url, q, **kwargs), LOOP)
    chunk_or_exception = q.get()
    while chunk_or_exception is not None:
        if isinstance(chunk_or_exception, Exception):
            raise chunk_or_exception
        yield chunk_or_exception
        chunk_or_exception = q.get()
    return future.result()


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


@atexit.register
def done():
    """Close all HTTP client

    Avoid a warning at exit
    """
    global LOOP

    async def close_client(client):
        try:
            await client.aclose()
        except httpx.HTTPError:
            pass

    async def close_clients():
        await asyncio.gather(*[close_client(client) for client in CLIENTS.values()], return_exceptions=False)
    future = asyncio.run_coroutine_threadsafe(close_clients(), LOOP)
    # wait 3 seconds to close the HTTP clients
    future.result(3)


init()
