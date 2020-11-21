from time import time
from urllib.parse import urlparse
from dictionary_client import DictionaryClient
from threading import local

import requests
import socks

from searx import settings

proxyTypes = dict(
    socks5=socks.SOCKS5,
    socks4=socks.SOCKS4,
    http=socks.HTTP
)

threadLocal = local()
connect = settings['outgoing'].get('pool_connections', 100)  # Magic number kept from previous code
maxsize = settings['outgoing'].get('pool_maxsize', requests.adapters.DEFAULT_POOLSIZE)  # Picked from constructor

def dict_request(method, query, **kwargs):
    time_before_request = time()

    # timeout
    if 'timeout' in kwargs:
        timeout = kwargs['timeout']
    else:
        timeout = getattr(threadLocal, 'timeout', None)
        if timeout is not None:
            kwargs['timeout'] = timeout

    dc = DictionaryClient(host=kwargs['host'], port=kwargs['port'], sock_class=socks.socksocket)

    # get proxy config
    proxies = kwargs.get('proxies')
    if proxies is None:
        proxies = settings['outgoing'].get('proxies')
    if proxies is not None and 'dict' in proxies:
        parsedProxy = urlparse(proxies['dict'])
        proxyType = proxyTypes.get(parsedProxy.scheme, None)
        dc.sock.setProxy(proxyType, parsedProxy.hostname, parsedProxy.port)

    # map available dict methods
    dict_methods = dict(
        define=dc.define,
        match=dc.match
    )
    dict_response = dict_methods.get(method)(query, db=kwargs['db'])
    response = dict(
        content=dict_response.content,
        databases=dc.databases
    )

    # request finished here
    time_after_request = time()

    # is there a timeout for this engine ?
    if timeout is not None:
        timeout_overhead = 0.2  # seconds
        # start_time = when the user request started
        start_time = getattr(threadLocal, 'start_time', time_before_request)
        search_duration = time_after_request - start_time
        if search_duration > timeout + timeout_overhead:
            raise requests.exceptions.Timeout(response=response)

    dc.disconnect()

    if hasattr(threadLocal, 'total_time'):
        threadLocal.total_time += time_after_request - time_before_request

    return response


def dict_define(query, **kwargs):
    return dict_request('define', query, **kwargs)
