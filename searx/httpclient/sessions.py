# -*- coding: utf-8 -*-
import pycurl
import threading
import concurrent.futures
from uuid import uuid4
from itertools import cycle, chain
from searx.httpclient.misc import HAS_HTTP2
from searx.httpclient.utils import logger
from searx.httpclient.models import PreparedResponse, Request, DEFAULT_REDIRECT_LIMIT
from searx.httpclient import exceptions


class FutureResponse(concurrent.futures.Future):

    __slots__ = 'request', 'curl_handler'

    def __init__(self, request, curl_handler):
        super(FutureResponse, self).__init__()
        self.request = request
        self.curl_handler = curl_handler
        self._prepare_response = PreparedResponse(request, curl_handler)

    def _finish(self, err_code=None, err_string=None):
        (result, exception) = self._prepare_response.finish(err_code, err_string)
        if exception:
            self.set_exception(exception)
        if result:
            self.set_result(result)

    def _get_user_object(self):
        return self

    def result(self, timeout=None):
        if timeout is None:
            timeout = self._prepare_response.get_remaining_time()
        try:
            return super(FutureResponse, self).result(timeout)
        except concurrent.futures.TimeoutError:
            raise exceptions.TimeoutError(request=self.request)

    def exception(self, timeout=None):
        if timeout is None:
            timeout = self._prepare_response.get_remaining_time()
        try:
            return super(FutureResponse, self).exception(timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(request=self.request)


class ConnectionPool(object):

    __slots__ = 'curl_share', 'max_connections', 'connections'

    def __init__(self, curl_share, max_connections):
        self.curl_share = curl_share
        self.max_connections = max_connections or 100  # Magic number from previous versions
        self.connections = []
        for i in range(max(100, self.max_connections)):
            h = self._new_connection()
            # add to the pool
            self.connections.append(h)

    def _new_connection(self):
        h = pycurl.Curl()
        h.setopt(pycurl.SHARE, self.curl_share)
        return h

    def borrowConnection(self, source_address=None):
        try:
            h = self.connections.pop()
        except:
            h = self._new_connection()
        # use source_addresses
        if source_address:
            h.setopt(pycurl.INTERFACE, source_address)
        return h

    def returnConnection(self, connection):
        connection.reset()
        self.connections.append(connection)


class Session(object):

    def __init__(self, start=True, share_cookies=True, source_ips=None, http2=True,
                 max_total_connections=None, max_host_connections=None):
        self.source_ips = cycle(source_ips) if source_ips else cycle([None])
        self.stream = False
        self.verify = True
        self.proxies = {}
        self.max_redirects = DEFAULT_REDIRECT_LIMIT
        # Ignore http2 parameter if curl doesn't support HTTP2
        self.http2 = http2 & HAS_HTTP2

        self.run = False
        self._future_responses = {}
        self._new_future_responses = []
        self._mutex = threading.Lock()
        self._no_new_future_response = threading.Condition(self._mutex)

        self.curl_share = pycurl.CurlShare()
        self.curl_share.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_DNS)
        self.curl_share.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_SSL_SESSION)
        if share_cookies:
            # FIXME: not tested
            self.curl_share.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_COOKIE)

        self._curl_multi_handler = pycurl.CurlMulti()
        if http2:
            # PIPE_MULTIPLEX: libcurl will attempt to re-use existing HTTP/2 connections
            # and just add a new stream over that when doing subsequent parallel requests.
            self._curl_multi_handler.setopt(pycurl.M_PIPELINING, pycurl.PIPE_MULTIPLEX)
        elif curl_version_ge(7, 62, 0):
            # https://daniel.haxx.se/blog/2019/04/06/curl-says-bye-bye-to-pipelining/
            self._curl_multi_handler.setopt(pycurl.M_PIPELINING, pycurl.PIPE_NOTHING)
        else:
            self._curl_multi_handler.setopt(pycurl.M_PIPELINING, pycurl.PIPE_HTTP1)
        if max_host_connections is not None:
            self._curl_multi_handler.setopt(pycurl.M_MAX_HOST_CONNECTIONS, max_host_connections)
        if max_total_connections is not None:
            self._curl_multi_handler.setopt(pycurl.M_MAX_TOTAL_CONNECTIONS, max_total_connections)
        self._connections = ConnectionPool(self.curl_share, max_total_connections)
        if start:
            self.start()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()

    def start(self):
        if not self.run:
            main_thread_name = 'httpclient-' + uuid4().__str__()
            self.run = True
            self.main_thread = threading.Thread(target=self.loop, name=main_thread_name)
            self.main_thread.daemon = True
            self.main_thread.start()

    def stop(self):
        if hasattr(self, 'run') and self.run:
            self.run = False
            with self._no_new_future_response:
                self._no_new_future_response.notify()
            self.main_thread.join(10.0)

    def close(self):
        self.stop()
        if hasattr(self, '_curl_multi_handler'):
            self._curl_multi_handler.close()

    def __del__(self):
        self.close()

    def _new_async_response(self, request, handle):
        return FutureResponse(request, handle)

    def async_request(self, method, url, **kwargs):
        kwargs.setdefault('stream', self.stream)
        kwargs.setdefault('verify', self.verify)
        kwargs.setdefault('proxies', self.proxies)
        kwargs.setdefault('max_redirects', self.max_redirects)
        kwargs.setdefault('http2', self.http2)
        request = Request(method=method, url=url, **kwargs)
        handle = self._connections.borrowConnection(next(self.source_ips))
        future_response = self._new_async_response(request, handle)
        with self._no_new_future_response:
            self._new_future_responses.append(future_response)
            self._no_new_future_response.notify()
        return future_response._get_user_object()

    def request(self, method, url, **kwargs):
        async_response = self.async_request(method, url, **kwargs)
        return async_response.result()

    def loop(self):
        handle_count = 0
        while self.run:
            # add new requests
            if handle_count == 0:
                with self._no_new_future_response:
                    self._no_new_future_response.wait()
            while len(self._new_future_responses) > 0:
                future_response = self._new_future_responses.pop()
                try:
                    self._curl_multi_handler.add_handle(future_response.curl_handler)
                    self._future_responses[future_response.curl_handler] = future_response
                except Exception as e:
                    logger.exception("Error adding request", e)
                    future_response._finish(-1, "Error adding request")
                    # safety net (?): do not reuse curl handle
                    future_response.curl_handler.close()

            # select
            self._curl_multi_handler.select(1)

            # perform
            while True:
                ret, handle_count = self._curl_multi_handler.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break

            # parse
            while True:
                num_q, success_list, error_list = self._curl_multi_handler.info_read()
                for handle in success_list:
                    future_response = self._future_responses[handle]
                    future_response._finish(None, None)
                    del self._future_responses[handle]
                    self._connections.returnConnection(handle)
                    self._curl_multi_handler.remove_handle(handle)
                for handle, err_code, err_string in error_list:
                    future_response = self._future_responses[handle]
                    future_response._finish(err_code, err_string)
                    del self._future_responses[handle]
                    self._connections.returnConnection(handle)
                    self._curl_multi_handler.remove_handle(handle)
                if num_q == 0:
                    break
