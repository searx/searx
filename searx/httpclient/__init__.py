# -*- coding: utf-8 -*-
# pycurl with the requests API
# borrow code from https://github.com/psf/requests
# borrow code from https://github.com/Lispython/human_curl/blob/master/human_curl/core.py ( Alexandr Lispython )
import sys
import searx.httpclient.misc

from searx.httpclient.exceptions import (HTTPError, RequestError, InvalidURLError,
                                         MissingSchemaError, InvalidMethodError,
                                         TimeoutError, ConnectionError, CurlError,
                                         SSLError, TooManyRedirects, ProxyError)

from searx.httpclient.requests import (set_timeout_for_thread, reset_time_for_thread,
                                       get_time_for_thread, request, get, post, head,
                                       options, delete, patch, put)

from searx.httpclient.models import (Request, Response)

from searx.httpclient.sessions import Session
if sys.version_info[0] == 3 and sys.version_info[1] >= 6:
    from searx.httpclient.asynciosessions import AsyncioSession
