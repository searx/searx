# -*- coding: utf-8 -*-
import pycurl


class HTTPError(Exception):
    "Base exception used by this module."
    pass


class RequestError(IOError):
    """There was an ambiguous exception that occurred while handling your
    request.
    """

    def __init__(self, *args, **kwargs):
        """Initialize RequestException with `request` and `response` objects."""
        response = kwargs.pop('response', None)
        self.response = response
        self.request = kwargs.pop('request', None)
        if (response is not None and not self.request and
                hasattr(response, 'request')):
            self.request = self.response.request
        self.err_code = kwargs.pop('err_code', None)
        self.err_string = kwargs.pop('err_string', None)
        self.message = self.__repr__()
        super(RequestError, self).__init__(*args)

    def __repr__(self):
        if hasattr(self, 'request'):
            req = 'request({0} "{1}")'.format(self.request.method, self.request.url)
        else:
            req = None
        if hasattr(self, 'response') and hasattr(self.response, 'status_code'):
            res = 'response({0})'.format(self.response.status_code)
        else:
            res = None
        if hasattr(self, 'err_code') and hasattr(self, 'err_string') and self.err_code is not None:
            err = 'cURL error({0}): {1}'.format(self.err_code, self.err_string)
        else:
            err = None
        return ', '.join(filter(None, (req, res, err)))

    def __str__(self):
        return self.__repr__()


class InvalidURLError(RequestError, ValueError):
    """The URL provided was somehow invalid."""


class MissingSchemaError(RequestError, ValueError):
    """The URL schema (e.g. http or https) is missing."""


class InvalidMethodError(RequestError, ValueError):
    """The method is invalid"""


class TimeoutError(RequestError):
    """Timeout exception"""


class ConnectionError(RequestError):
    """A Connection error occurred."""


class CurlError(RequestError):
    """Curl error"""
    def __init__(self, *args, **kwargs):
        super(CurlError, self).__init__(*args, **kwargs)


class SSLError(RequestError):
    pass


class TooManyRedirects(RequestError):
    pass


class ProxyError(RequestError):
    pass


CURL_ERROR_CODE_TO_EXCEPTION = {
    pycurl.E_UNSUPPORTED_PROTOCOL: InvalidURLError,
    pycurl.E_URL_MALFORMAT: InvalidURLError,
    pycurl.E_COULDNT_RESOLVE_HOST: ConnectionError,
    pycurl.E_COULDNT_CONNECT: ConnectionError,
    pycurl.E_OPERATION_TIMEDOUT: TimeoutError,
    pycurl.E_SSL_CONNECT_ERROR: SSLError,
    pycurl.E_TOO_MANY_REDIRECTS: TooManyRedirects,
    pycurl.E_SSL_CERTPROBLEM: SSLError,
    pycurl.E_SSL_CIPHER: SSLError,
    pycurl.E_SSL_ISSUER_ERROR: SSLError,
    pycurl.E_COULDNT_RESOLVE_PROXY: ProxyError
}
