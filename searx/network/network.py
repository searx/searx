# SPDX-License-Identifier: AGPL-3.0-or-later

import atexit
import asyncio
import ipaddress
from itertools import cycle

import httpx

from searx import settings, engines
from .client import new_client, LOOP


DEFAULT_NAME = '__DEFAULT__'
NETWORKS = {}
# requests compatibility when reading proxy settings from settings.yml
PROXY_PATTERN_MAPPING = {
    'http': 'http://',
    'https': 'https://',
    'socks4': 'socks4://',
    'socks5': 'socks5://',
    'socks5h': 'socks5h://',
    'http:': 'http://',
    'https:': 'https://',
    'socks4:': 'socks4://',
    'socks5:': 'socks5://',
    'socks5h:': 'socks5h://',
}


class Network:

    __slots__ = ('enable_http', 'verify', 'http2',
                 'max_connections', 'max_keepalive_connections', 'keepalive_expiry',
                 'local_addresses', 'support_ipv4', 'support_ipv6', 'proxies', 'max_redirects', 'retries',
                 '_local_addresses_cycle', '_proxies_cycle', '_clients')

    def __init__(self,
                 enable_http=True,
                 verify=True,
                 http2=False,
                 max_connections=None,
                 max_keepalive_connections=None,
                 keepalive_expiry=None,
                 proxies=None,
                 local_addresses=None,
                 support_ipv4=True,
                 support_ipv6=True,
                 retries=0,
                 max_redirects=30):
        self.enable_http = enable_http
        self.verify = verify
        self.http2 = http2
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry
        self.proxies = proxies
        self.local_addresses = local_addresses
        self.support_ipv4 = support_ipv4
        self.support_ipv6 = support_ipv6
        self.retries = retries
        self.max_redirects = max_redirects
        self._local_addresses_cycle = self.get_ipaddress_cycle()
        self._proxies_cycle = self.get_proxy_cycles()
        self._clients = {}

    def is_valid_ipaddress(self, a):
        return (self.support_ipv6 and isinstance(a, ipaddress.IPv6Address)) \
            or (self.support_ipv4 and isinstance(a, ipaddress.IPv4Address))

    def get_ipaddress_cycle(self):
        while True:
            if not self.local_addresses:
                if self.support_ipv4 == self.support_ipv6:
                    yield None
                else:
                    # either self.support_ipv4 or self.support_ipv6 is False
                    if self.support_ipv4:
                        yield '0.0.0.0'
                    if self.support_ipv6:
                        yield '::'
            else:
                count = 0
                for address in self.local_addresses:
                    if '/' in address:
                        for a in ipaddress.ip_network(address).hosts():
                            if self.is_valid_ipaddress(a):
                                yield str(a)
                                count += 1
                    else:
                        a = ipaddress.ip_address(address)
                        if self.is_valid_ipaddress(a):
                            yield str(a)
                            count += 1
                if count == 0:
                    yield None

    def iter_proxies(self):
        if not self.proxies:
            return
        # https://www.python-httpx.org/compatibility/#proxy-keys
        if isinstance(self.proxies, str):
            yield 'all://', [self.proxies]
        elif isinstance(self.proxies, dict):
            for pattern, proxy_url in self.proxies.items():
                pattern = PROXY_PATTERN_MAPPING.get(pattern, pattern)
                if isinstance(proxy_url, str):
                    proxy_url = [proxy_url]
                yield pattern, proxy_url

    def get_proxy_cycles(self):
        proxy_settings = {}
        for pattern, proxy_urls in self.iter_proxies():
            proxy_settings[pattern] = cycle(proxy_urls)
        while True:
            yield tuple((pattern, next(proxy_url_cycle)) for pattern, proxy_url_cycle in proxy_settings.items())

    def get_client(self, verify=None, max_redirects=None):
        verify = self.verify if verify is None else verify
        max_redirects = self.max_redirects if max_redirects is None else max_redirects
        local_address = next(self._local_addresses_cycle)
        proxies = next(self._proxies_cycle)  # is a tuple so it can be part of key
        key = (verify, max_redirects, local_address, proxies)
        if key not in self._clients:
            self._clients[key] = new_client(self.enable_http,
                                            verify,
                                            self.http2,
                                            self.max_connections,
                                            self.max_keepalive_connections,
                                            self.keepalive_expiry,
                                            dict(proxies),
                                            local_address,
                                            0,
                                            max_redirects)
        return self._clients[key]

    async def aclose(self):
        async def close_client(client):
            try:
                await client.aclose()
            except httpx.HTTPError:
                pass
        await asyncio.gather(*[close_client(client) for client in self._clients.values()], return_exceptions=False)

    @staticmethod
    def get_kwargs_clients(kwargs):
        kwargs_clients = {}
        if 'verify' in kwargs:
            kwargs_clients['verify'] = kwargs.pop('verify')
        if 'max_redirects' in kwargs:
            kwargs_clients['max_redirects'] = kwargs.pop('max_redirects')
        return kwargs_clients

    async def request(self, method, url, **kwargs):
        retries = self.retries
        while retries >= 0:
            kwargs_clients = Network.get_kwargs_clients(kwargs)
            client = self.get_client(**kwargs_clients)
            try:
                return await client.request(method, url, **kwargs)
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if retries <= 0:
                    raise e
            retries -= 1

    def stream(self, method, url, **kwargs):
        retries = self.retries
        while retries >= 0:
            kwargs_clients = Network.get_kwargs_clients(kwargs)
            client = self.get_client(**kwargs_clients)
            try:
                return client.stream(method, url, **kwargs)
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if retries <= 0:
                    raise e
            retries -= 1


def get_network(name=None):
    global NETWORKS
    return NETWORKS[name or DEFAULT_NAME]


def initialize(settings_engines=None, settings_outgoing=None):
    global NETWORKS, engines

    settings_engines = settings_engines or settings.get('engines')
    settings_outgoing = settings_outgoing or settings.get('outgoing')

    # default parameters for AsyncHTTPTransport
    # see https://github.com/encode/httpx/blob/e05a5372eb6172287458b37447c30f650047e1b8/httpx/_transports/default.py#L108-L121  # noqa
    default_params = {
        'enable_http': False,
        'verify': True,
        'http2': settings_outgoing.get('http2', False),
        # Magic number kept from previous code
        'max_connections': settings_outgoing.get('pool_connections', 100),
        # Picked from constructor
        'max_keepalive_connections': settings_outgoing.get('pool_maxsize', 10),
        #
        'keepalive_expiry': settings_outgoing.get('keepalive_expiry', 5.0),
        'local_addresses': settings_outgoing.get('source_ips'),
        'support_ipv4': settings_outgoing.get('support_ipv4'),
        'support_ipv6': settings_outgoing.get('support_ipv6'),
        'proxies': settings_outgoing.get('proxies'),
        # default maximum redirect
        # from https://github.com/psf/requests/blob/8c211a96cdbe9fe320d63d9e1ae15c5c07e179f8/requests/models.py#L55
        'max_redirects': 30,
        #
        'retries': 0,
    }

    def new_network(params):
        nonlocal default_params
        result = {}
        result.update(default_params)
        result.update(params)
        return Network(**result)

    def iter_networks():
        nonlocal settings_engines
        for engine_spec in settings_engines:
            engine_name = engine_spec['name']
            engine = engines.engines.get(engine_name)
            if engine is None:
                continue
            network = getattr(engine, 'network', None)
            yield engine_name, engine, network

    NETWORKS.clear()
    NETWORKS[DEFAULT_NAME] = new_network({})

    # define networks from outgoing.networks
    for network_name, network in settings_outgoing.get('networks', {}).items():
        NETWORKS[network_name] = new_network(network)

    # define networks from engines.[i].network (except references)
    for engine_name, engine, network in iter_networks():
        if network is None:
            network = {}
            for attribute_name in default_params:
                if hasattr(engine, attribute_name):
                    network[attribute_name] = getattr(engine, attribute_name)
                elif attribute_name in default_params:
                    network[attribute_name] = default_params[attribute_name]
            NETWORKS[engine_name] = new_network(network)
        elif isinstance(network, dict):
            NETWORKS[engine_name] = new_network(network)

    # define networks from engines.[i].network (references)
    for engine_name, engine, network in iter_networks():
        if isinstance(network, str):
            NETWORKS[engine_name] = NETWORKS[network]


@atexit.register
def done():
    """Close all HTTP client

    Avoid a warning at exit
    see https://github.com/encode/httpx/blob/1a6e254f72d9fd5694a1c10a28927e193ab4f76b/httpx/_client.py#L1785

    Note: since Network.aclose has to be async, it is not possible to call this method on Network.__del__
    So Network.aclose is called here using atexit.register
    """
    global LOOP

    async def close_networks():
        await asyncio.gather(*[network.aclose() for network in NETWORKS.values()], return_exceptions=False)
    if LOOP:
        future = asyncio.run_coroutine_threadsafe(close_networks(), LOOP)
        # wait 3 seconds to close the HTTP clients
        future.result(3)


NETWORKS[DEFAULT_NAME] = Network()
