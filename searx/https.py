from searx import logger

import ssl
import requests
import requests.packages.urllib3.contrib.pyopenssl
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

from itertools import cycle
from threading import RLock
from searx import settings
from searx.exceptions import SearxNetworkException

# see https://github.com/shazow/urllib3/blob/master/urllib3/util/ssl_.py
# - Prefer TLS 1.3 cipher suites
# - prefer cipher suites that offer perfect forward secrecy (DHE/ECDHE),
# - prefer ECDHE over DHE for better performance,
#
# AES256-GCM-SHA384 for www.ebi.ac.uk, api.base-search.net, gigablast.com
CIPHERS = ':'.join([
    'TLS13-AES-256-GCM-SHA384',
    'TLS13-AES-128-GCM-SHA256',
    'TLS13-CHACHA20-POLY1305-SHA256',
    'ECDHE-ECDSA-AES256-GCM-SHA384',
    'ECDHE-RSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-CHACHA20-POLY1305',
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-AES256-SHA384',
    'ECDHE-RSA-AES256-SHA384',
    'ECDHE-ECDSA-AES128-SHA256',
    'ECDHE-RSA-AES128-SHA256',
    'AES256-GCM-SHA384',
    '!aNULL',
    '!eNULL',
    '!MD5',
])

# disable SSL2/3, TLS1, TLS1.1 and compression
SSL_OPTIONS = ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_COMPRESSION


class SearxHTTPAdapter(requests.adapters.HTTPAdapter):

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

        context = create_urllib3_context(ciphers=CIPHERS, options=SSL_OPTIONS)
        conn_params['ssl_context'] = context

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

        context = create_urllib3_context(ciphers=CIPHERS, options=SSL_OPTIONS)
        self._conn_params['ssl_context'] = context

        self.init_poolmanager(self._pool_connections, self._pool_maxsize,
                              block=self._pool_block, **self._conn_params)


class SearxUnsecureHTTPAdapter(SearxHTTPAdapter):

    def send(self, request, *args, **kwargs):
        url_withouthttp = request.url[7:]  # remove http://
        host = url_withouthttp.split('/')[0].split('?')[0]
        logger.warn("unsecure HTTP request to " + host)
        response = super(SearxUnsecureHTTPAdapter, self).send(request, *args, **kwargs)
        response.unsecure = True
        # FIXME : hook requests.sessions.SessionRedirectMixin.rebuild_method to make unsecure http to https redirect
        # look at the response.history[i].unsecure
        return response


connect = settings['outgoing'].get('pool_connections', 100)  # Magic number kept from previous code
maxsize = settings['outgoing'].get('pool_maxsize', requests.adapters.DEFAULT_POOLSIZE)  # Picked from constructor
if settings['outgoing'].get('source_ips'):
    http_adapters = cycle(SearxUnsecureHTTPAdapter(pool_connections=connect, pool_maxsize=maxsize,
                                                   source_address=(source_ip, 0))
                          for source_ip in settings['outgoing']['source_ips'])
    https_adapters = cycle(SearxHTTPAdapter(pool_connections=connect, pool_maxsize=maxsize,
                                            source_address=(source_ip, 0))
                           for source_ip in settings['outgoing']['source_ips'])
else:
    http_adapters = cycle((SearxUnsecureHTTPAdapter(pool_connections=connect, pool_maxsize=maxsize), ))
    https_adapters = cycle((SearxHTTPAdapter(pool_connections=connect, pool_maxsize=maxsize), ))


class SessionSinglePool(requests.Session):

    def __init__(self):
        super(SessionSinglePool, self).__init__()

        # reuse the same adapters
        with RLock():
            self.adapters.clear()
            self.mount('https://', next(https_adapters))
            self.mount('http://', next(http_adapters))

    def close(self):
        """Call super, but clear adapters since they are managed globaly"""
        self.adapters.clear()
        super(SessionSinglePool, self).close()


def request(method, url, **kwargs):
    """same as requests/requests/api.py request(...) except it use SessionSinglePool and force proxies"""
    session = SessionSinglePool()
    kwargs['proxies'] = settings['outgoing'].get('proxies', None)
    response = session.request(method=method, url=url, **kwargs)
    session.close()
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
