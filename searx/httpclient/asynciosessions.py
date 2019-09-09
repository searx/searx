# -*- coding: utf-8 -*-
import asyncio
import pycurl
from searx.httpclient.sessions import Session
from searx.httpclient.models import PreparedResponse


class AsyncioFutureResponse(object):

    def __init__(self, request, curl_handler, loop):
        self.request = request
        self.curl_handler = curl_handler
        self._loop = loop
        self._future = loop.create_future()
        self._prepare_response = PreparedResponse(request, curl_handler)

    def _finish(self, err_code=None, err_string=None):
        (result, exception) = self._prepare_response.finish(err_code, err_string)
        if exception:
            self._loop.call_soon_threadsafe(self._future.set_exception, exception)
        if result:
            self._loop.call_soon_threadsafe(self._future.set_result, result)

    def _get_user_object(self):
        return self._future


class AsyncioSession(Session):

    def __init__(self, loop=None, **kwargs):
        super(AsyncioSession, self).__init__(**kwargs)
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

    def _new_async_response(self, request, handle):
        return AsyncioFutureResponse(request, handle, self._loop)

    async def request(self, method, url, **kwargs):
        async_response = self.async_request(method, url, **kwargs)
        return await async_response.result()
