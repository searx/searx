# -*- coding: utf-8 -*-
import sys
import pycurl
import certifi
import cgi
import time
import logging
import cchardet as chardet
from itertools import chain
from re import compile as re_compile
from searx.url_utils import urlencode, urljoin, urlparse, urlunparse, quote
from searx.utils import basestring, to_key_val_list, IS_PY2
from searx.httpclient.utils import logger, unquote_unreserved, to_native_string, CaseInsensitiveDict
from searx.httpclient.misc import curl_version_ge, HAS_HTTP2
from searx.httpclient import exceptions

# searx: always use unicode (is str with python3)
# requests: always use str (is unicode with python2)
# use requests convention here
if sys.version_info[0] == 2:
    str = unicode

try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

try:
    import simplejson as json
except ImportError:
    import json

try:
    from http.cookies import SimpleCookie, CookieError
except ImportError:
    from Cookie import SimpleCookie, CookieError


# from https://github.com/psf/requests/blob/428f7a275914f60a8f1e76a7d69516d617433d30/requests/models.py#L55
DEFAULT_REDIRECT_LIMIT = 30
CERTIFI_PATH = certifi.where()
# from https://github.com/Lispython/human_curl/blob/1bdda958c4bb57f73f2332bfef5026a44270b3c3/human_curl/core.py#L61
HTTP_GENERAL_RESPONSE_HEADER = re_compile(r"(?P<version>HTTP\/.*?)\s+(?P<code>\d{3})\s+(?P<message>.*)")

TO_CURL_HTTP_METHOD = {
    "GET": pycurl.HTTPGET,
    "POST": pycurl.POST,
    # "PUT": pycurl.UPLOAD,
    "PUT": pycurl.PUT,
    "HEAD": pycurl.NOBODY
}
SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE", "PUT", "OPTIONS")

# FULL LIST OF GETINFO OPTIONS
CURL_INFO_MAP = {
    # timers
    # An overview of the six time values available from curl_easy_getinfo()
    # perform() --> NAMELOOKUP --> CONNECT --> APPCONNECT
    # --> PRETRANSFER --> STARTTRANSFER --> TOTAL --> REDIRECT
    "TOTAL_TIME": pycurl.TOTAL_TIME,
    "NAMELOOKUP_TIME": pycurl.NAMELOOKUP_TIME,
    "CONNECT_TIME": pycurl.CONNECT_TIME,
    "APPCONNECT_TIME": pycurl.APPCONNECT_TIME,
    "PRETRANSFER_TIME": pycurl.PRETRANSFER_TIME,
    "STARTTRANSFER_TIME": pycurl.STARTTRANSFER_TIME,
    "REDIRECT_TIME": pycurl.REDIRECT_TIME,
}

# PROXY
PROXIES_TYPES_MAP = {
    'socks5-hostname': pycurl.PROXYTYPE_SOCKS5_HOSTNAME,
    'socks5': pycurl.PROXYTYPE_SOCKS5,
    'socks4': pycurl.PROXYTYPE_SOCKS4,
    'socks4a': pycurl.PROXYTYPE_SOCKS4A,
    'http': pycurl.PROXYTYPE_HTTP,
    'https': pycurl.PROXYTYPE_HTTP
}

# HTTPVERSION
CURL_HTTPVERSION_MAP = {
    pycurl.CURL_HTTP_VERSION_1_0: "HTTP/1.0",
    pycurl.CURL_HTTP_VERSION_1_1: "HTTP/1.1",
}

if HAS_HTTP2:
    CURL_HTTPVERSION_MAP[pycurl.CURL_HTTP_VERSION_2_0] = "HTTP/2"


class PreparedResponse(object):

    __slots__ = 'request', 'curl_handler', 'start_time', '_response_buffer', '_response_headers'

    def __init__(self, request, curl_handler):
        if request.stream:
            raise NotImplementedError()
        PrepareCurlHandler.prepare_curl_handler(request, curl_handler)
        self.request = request
        self.curl_handler = curl_handler
        self.start_time = time.time()
        self._response_headers = BytesIO()
        curl_handler.setopt(pycurl.WRITEHEADER, self._response_headers)
        self._response_buffer = BytesIO()
        curl_handler.setopt(pycurl.WRITEDATA, self._response_buffer)

    def get_remaining_time(self):
        return max(0.0, self.request.timeout - (time.time() - self.start_time)) / 1000.0

    # from https://github.com/Lispython/human_curl/blob/1bdda958c4bb57f73f2332bfef5026a44270b3c3/human_curl/core.py#L695
    def _get_curl_info(self):
        curl_handler = self.curl_handler
        response_info = {}
        for field, value in CURL_INFO_MAP.items():
            try:
                field_data = curl_handler.getinfo(value)
            except Exception as e:
                logger.warn("getinfo({0}) error".format(field), e)
                continue
            else:
                response_info[field] = field_data
        return response_info

    def finish(self, err_code=None, err_string=None):
        response = None
        exception = None
        curl_handler = self.curl_handler
        try:
            content_type = curl_handler.getinfo(pycurl.CONTENT_TYPE)
        except:
            content_type = None
        try:
            url = curl_handler.getinfo(pycurl.EFFECTIVE_URL)
            content = self._response_buffer.getvalue()
            headers_raw = self._response_headers.getvalue()
            status_code = curl_handler.getinfo(pycurl.HTTP_CODE)
            info = self._get_curl_info()
            elapsed = time.time() - self.start_time
            response = Response(self.request, url, content, status_code, headers_raw, content_type, info, elapsed)
            if logger.isEnabledFor(logging.DEBUG):
                http_version = CURL_HTTPVERSION_MAP.get(curl_handler.getinfo(pycurl.INFO_HTTP_VERSION), "HTTP?")
                download_size = int(curl_handler.getinfo(pycurl.SIZE_DOWNLOAD))
                logger.debug("\"{12} {0} {10}\" {9} {11}\n  total: {1:.3f}s, pycurl: {2:.3f}s, namelookup: {3:.3f}s, "
                             "connect: {4:.3f}s, appconnect: {5:.3f}s, pretransfer: {6:.3f}s, "
                             "starttransfer: {7:.3f}s, redirect: {8:.3f}s".format(
                                 url, elapsed, info["TOTAL_TIME"],
                                 info["NAMELOOKUP_TIME"], info["CONNECT_TIME"], info["APPCONNECT_TIME"],
                                 info["PRETRANSFER_TIME"], info["STARTTRANSFER_TIME"], info["REDIRECT_TIME"],
                                 status_code, http_version, download_size, self.request.method.upper()))
            if err_code is not None:
                logger.error("cURL error ({0}): {1} {2}".format(err_code, err_string, curl_handler.errstr()))
                error = exceptions.CURL_ERROR_CODE_TO_EXCEPTION.get(err_code, exceptions.CurlError)
                exception = error(response=response, request=self.request,
                                  err_code=err_code, err_string=err_string)
        except Exception as e:
            logger.error(e)
            exception = e
        finally:
            self._response_buffer.close()
            self._response_headers.close()
        return (response, exception)


class PrepareCurlHandler(object):

    @staticmethod
    def prepare_curl_handler(request, curl_handler):
        # no SIGNAL (seems to slow down request by about 100ms ?)
        curl_handler.setopt(pycurl.NOSIGNAL, 1)

        # wait for pipe connection to confirm
        if curl_version_ge(7, 43, 0):
            curl_handler.setopt(pycurl.PIPEWAIT, True)

        # consistently use ipv4
        curl_handler.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)

        # TCP FastOpen
        if curl_version_ge(7, 49, 0):
            curl_handler.setopt(pycurl.TCP_FASTOPEN, True)

        # TCP KeepAlive
        if curl_version_ge(7, 25, 0):
            curl_handler.setopt(pycurl.TCP_KEEPALIVE, True)
            curl_handler.setopt(pycurl.TCP_KEEPIDLE, 30)
            curl_handler.setopt(pycurl.TCP_KEEPINTVL, 15)

        # use TLS1.3 if possible
        # curl_handler.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_MAX_TLSv1_3)

        # see https://curl.haxx.se/docs/http2.html
        if request.http2:
            curl_handler.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2TLS)
        else:
            curl_handler.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)

        # use certifi
        curl_handler.setopt(pycurl.CAINFO, CERTIFI_PATH)

        # verify certificate ?
        if request.verify:
            curl_handler.setopt(pycurl.SSL_VERIFYPEER, 1)
            curl_handler.setopt(pycurl.SSL_VERIFYHOST, 2)
        else:
            curl_handler.setopt(pycurl.SSL_VERIFYPEER, 0)
            curl_handler.setopt(pycurl.SSL_VERIFYHOST, 0)

        # set debug
        curl_handler.setopt(pycurl.VERBOSE, request.debug)

        # xferinfo function
        if request.xferinfo_function is not None:
            if curl_version_ge(7, 32, 0):
                curl_handler.setopt(pycurl.NOPROGRESS, False)
                curl_handler.setopt(pycurl.XFERINFOFUNCTION, request.xferinfo_function)
            else:
                # FIXME
                pass
        else:
            curl_handler.setopt(pycurl.NOPROGRESS, True)

        # set url
        url, scheme, hostname = PrepareCurlHandler._prepare_url(request.url, request.params)
        curl_handler.setopt(curl_handler.URL, url)

        # Follow redirects
        if request.allow_redirects:
            curl_handler.setopt(pycurl.FOLLOWLOCATION, True)
            curl_handler.setopt(pycurl.MAXREDIRS, DEFAULT_REDIRECT_LIMIT)
        else:
            curl_handler.setopt(pycurl.FOLLOWLOCATION, False)

        # cURL automaticaly add supported encoding (since curl 7.21.6)
        curl_handler.setopt(curl_handler.ACCEPT_ENCODING, '')

        # set timeout
        curl_handler.setopt(curl_handler.CONNECTTIMEOUT_MS, int(request.timeout))
        curl_handler.setopt(curl_handler.TIMEOUT_MS, int(request.timeout))

        # set data
        if request.data is not None:
            curl_handler.setopt(curl_handler.POSTFIELDS, urlencode(request.data))

        # Method
        method = request.method.upper()
        if method in TO_CURL_HTTP_METHOD.values():
            curl_handler.setopt(TO_CURL_HTTP_METHOD[method], True)
        elif method in SUPPORTED_METHODS:
            curl_handler.setopt(pycurl.CUSTOMREQUEST, method)
        else:
            raise exceptions.InvalidMethodError("cURL request do not support %s" % method)

        # Method: Responses without body
        if method in ("OPTIONS", "HEAD", "DELETE"):
            curl_handler.setopt(pycurl.NOBODY, True)

        # Headers
        curl_handler.setopt(pycurl.HTTPHEADER,
                            ['{0}: {1}'.format(k, v)
                             for k, v in request.headers.items()])

        # Cookies
        if request.cookies:
            curl_handler.setopt(pycurl.COOKIE, '; '.join('{0}={1}'.format(k, v)
                                for k, v in request.cookies.items()))
        else:
            curl_handler.unsetopt(pycurl.COOKIE)

        # Proxy
        if request.proxies:
            proxy = PrepareCurlHandler.select_proxy(scheme, hostname, request.proxies)
            if proxy is not None:
                pscheme, pnetloc = proxy.split('://')
                ptype = PROXIES_TYPES_MAP.get(pscheme.lower())
                if ptype is not None:
                    curl_handler.setopt(pycurl.PROXYTYPE, ptype)
                    curl_handler.setopt(pycurl.PROXY, pnetloc)
                else:
                    raise exceptions.ProxyError(request=request)
            else:
                curl_handler.unsetopt(pycurl.PROXYTYPE)
                curl_handler.unsetopt(pycurl.PROXY)

    # modified version of https://github.com/psf/requests/blob/428f7a275914f60a8f1e76a7d69516d617433d30/requests/models.py#L356 # noqa
    @staticmethod
    def _prepare_url(url, params):
        """Prepares the given HTTP URL."""
        #: Accept objects that have string representations.
        #: We're unable to blindly call unicode/str functions
        #: as this will include the bytestring indicator (b'')
        #: on python 3.x.
        #: https://github.com/psf/requests/pull/2238
        if isinstance(url, bytes):
            url = url.decode('utf8')
        else:
            url = unicode(url) if IS_PY2 else str(url)

        # Remove leading whitespaces from url
        url = url.lstrip()

        # Don't do any URL preparation for non-HTTP schemes like `mailto`,
        # `data` etc to work around exceptions from `url_parse`, which
        # handles RFC 3986 only.
        if ':' in url and not url.lower().startswith('http'):
            return url

        # Support for unicode domain names and paths.
        try:
            r = urlparse(url)
            scheme, netloc, path, query, fragment, hostname = \
                r.scheme, r.netloc, r.path, r.query, r.fragment, r.hostname
        except ValueError as e:
            raise exceptions.InvalidURLError(*e.args)

        if not scheme:
            error = "Invalid URL {0!r}: No schema supplied. Perhaps you meant http://{0}?"
            error = error.format(to_native_string(url, 'utf8'))
            raise exceptions.MissingSchemaError(error)

        # check if there is a netloc
        if not netloc:
            raise exceptions.InvalidURLError("Invalid URL %r: No host supplied" % url)

        # Bare domains aren't valid URLs.
        if not path:
            path = '/'

        if IS_PY2:
            if isinstance(scheme, str):
                scheme = scheme.encode('utf-8')
            if isinstance(netloc, str):
                netloc = netloc.encode('utf-8')
            if isinstance(path, str):
                path = path.encode('utf-8')
            if isinstance(query, str):
                query = query.encode('utf-8')
            if isinstance(fragment, str):
                fragment = fragment.encode('utf-8')

        if isinstance(params, (str, bytes)):
            params = to_native_string(params)

        enc_params = PrepareCurlHandler._encode_params(params)
        if enc_params:
            if query:
                query = '%s&%s' % (query, enc_params)
            else:
                query = enc_params

        return (PrepareCurlHandler.requote_uri(
                urlunparse([scheme, netloc, path, None, query, fragment])),
                scheme,
                hostname)

    # from https://github.com/psf/requests/blob/428f7a275914f60a8f1e76a7d69516d617433d30/requests/models.py#L83
    @staticmethod
    def _encode_params(data):
        """Encode parameters in a piece of data.
        Will successfully encode parameters when passed as a dict or a list of
        2-tuples. Order is retained if data is a list of 2-tuples but arbitrary
        if parameters are supplied as a dict.
        """

        if isinstance(data, (str, bytes)):
            return data
        elif hasattr(data, 'read'):
            return data
        elif hasattr(data, '__iter__'):
            # speed optimization
            if len(data) == 0:
                return ''
            result = []
            for k, vs in to_key_val_list(data):
                if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append(
                            (k.encode('utf-8') if isinstance(k, str) else k,
                             v.encode('utf-8') if isinstance(v, str) else v))
            return urlencode(result, doseq=True)
        else:
            return data

    # from https://github.com/psf/requests/blob/3e7d0a873f838e0001f7ac69b1987147128a7b5f/requests/utils.py#L594
    @staticmethod
    def requote_uri(uri):
        """Re-quote the given URI.
        This function passes the given URI through an unquote/quote cycle to
        ensure that it is fully and consistently quoted.
        :rtype: str
        """
        safe_with_percent = "!#$%&'()*+,/:;=?@[]~"
        safe_without_percent = "!#$&'()*+,/:;=?@[]~"
        try:
            # Unquote only the unreserved characters
            # Then quote only illegal characters (do not quote reserved,
            # unreserved, or '%')
            return quote(unquote_unreserved(uri), safe=safe_with_percent)
        except exceptions.InvalidURLError:
            # We couldn't unquote the given URI, so let's try quoting it, but
            # there may be unquoted '%'s in the URI. We need to make sure they're
            # properly quoted so they do not cause issues elsewhere.
            return quote(uri, safe=safe_without_percent)

    # from https://github.com/psf/requests/blob/3e7d0a873f838e0001f7ac69b1987147128a7b5f/requests/utils.py
    @staticmethod
    def select_proxy(scheme, hostname, proxies):
        """Select a proxy for the url, if applicable.
        :param url: The url being for the request
        :param proxies: A dictionary of schemes or schemes and hosts to proxy URLs
        """
        if hostname is None:
            return proxies.get(scheme, proxies.get('all'))

        proxy_keys = [
            scheme + '://' + hostname,
            scheme,
            'all://' + hostname,
            'all',
        ]
        proxy = None
        for proxy_key in proxy_keys:
            if proxy_key in proxies:
                proxy = proxies[proxy_key]
                break

        return proxy


class Request(object):

    def __init__(self,
                 method=None,
                 url=None,
                 headers=None,
                 data=None,
                 params=None,
                 cookies=None,
                 stream=False,
                 allow_redirects=True,
                 max_redirects=0,
                 http2=True,
                 timeout=2.0,
                 verify=True,
                 proxies=None,
                 debug=False,
                 xferinfo_function=None):
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        if cookies is None:
            cookies = {}
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data
        self.params = params
        self.cookies = cookies
        self.stream = stream
        self.allow_redirects = allow_redirects
        self.max_redirects = max_redirects
        self.http2 = http2
        self.timeout = int(timeout * 1000)  # in milisecs
        self.verify = verify
        self.proxies = proxies
        self.debug = debug
        self.xferinfo_function = xferinfo_function

    def __repr__(self):
        return '<Request [%s]>' % (self.method)


# no __bool__ / __nonzero__ : https://github.com/psf/requests/issues/2002
class Response(object):

    def __init__(self, request, url, content, status_code, headers_raw, content_type, info, elapsed):
        self.request = request
        self.url = url
        self.content = content
        self._content_type = content_type
        self._headers_raw = headers_raw
        self.status_code = status_code
        self.info = info
        self.elapsed = elapsed
        self._reason = None
        self.encoding = self._encoding_from_content_type()
        # list of parsed headers blocks
        self._headers_history = []
        # Redirects history
        self._history = []
        # Headers
        self._headers = CaseInsensitiveDict()
        # Cookies
        self._cookies = {}

    # from https://github.com/Lispython/human_curl/blob/1bdda958c4bb57f73f2332bfef5026a44270b3c3/human_curl/core.py#L761
    @staticmethod
    def _split_headers_blocks(raw_headers):
        i = 0
        blocks = []
        for item in raw_headers.strip().split("\r\n"):
            if item.startswith("HTTP"):
                blocks.append([item])
                i = len(blocks) - 1
            elif item:
                blocks[i].append(item)
        return blocks

    def _encoding_from_content_type(self):
        if self._content_type:
            _, params = cgi.parse_header(self._content_type)
            charset = params.get('charset', None)
            if charset:
                return charset.lower()
            else:
                return None
        else:
            return None

    # modify version of https://github.com/Lispython/human_curl/blob/1bdda958c4bb57f73f2332bfef5026a44270b3c3/human_curl/core.py#L772 # noqa
    def _parse_headers_raw(self):
        """Parse response headers and save as instance vars
        """
        def parse_header_block(raw_block):
            r"""Parse headers block
            Arguments:
            - `block`: raw header block
            Returns:
            - `headers_list`:
            """
            block_headers = []
            for header in raw_block:
                if not header:
                    continue
                elif not header.startswith("HTTP"):
                    field, value = map(lambda u: u.strip(), header.split(":", 1))
                    if field.startswith("Location"):
                        # maybe not good
                        if not value.startswith("http"):
                            value = urljoin(self.url, value)
                        self._history.append(value)
                    if value[:1] == value[-1:] == '"':
                        value = value[1:-1]  # strip "
                    block_headers.append((field, value.strip()))
                elif header.startswith("HTTP"):
                    # extract version, code, message from first header
                    try:
                        version, code, message = HTTP_GENERAL_RESPONSE_HEADER.findall(header)[0]
                    except Exception as e:
                        # logger.warn(e)
                        continue
                    else:
                        block_headers.append((version, code, message))
                else:
                    # raise ValueError("Wrong header field")
                    pass
            return block_headers

        for raw_block in self._split_headers_blocks(self._headers_raw.decode('utf-8')):
            block = parse_header_block(raw_block)
            self._headers_history.append(block)

        last_header = self._headers_history[-1]
        self._reason = last_header[0][2]
        self._headers = CaseInsensitiveDict(last_header[1:])

        if not self._history:
            self._history.append(self.url)

        if not self.encoding:
            self.encoding = self._encoding_from_content_type()

    # from https://github.com/Lispython/human_curl/blob/1bdda958c4bb57f73f2332bfef5026a44270b3c3/human_curl/core.py#L825
    def _parse_cookies(self):
        if not self._headers_history:
            self._parse_headers_raw()

        # Get cookies from endpoint
        cookies = []
        for header in chain(*self._headers_history):
            if len(header) > 2:
                continue
            key, value = header[0], header[1]
            if key.lower().startswith("set-cookie"):
                try:
                    cookie = SimpleCookie()
                    cookie.load(value)
                    cookies.extend(cookie.values())
                except CookieError as e:
                    logger.warn("_parse_cookies error", e)
        self._cookies = dict([(cookie.key, cookie.value) for cookie in cookies])
        return self._cookies

    # from https://github.com/psf/requests/blob/428f7a275914f60a8f1e76a7d69516d617433d30/requests/models.py#L730
    @property
    def apparent_encoding(self):
        return chardet.detect(self.content)['encoding']

    # from https://github.com/psf/requests/blob/428f7a275914f60a8f1e76a7d69516d617433d30/requests/models.py#L854
    @property
    def text(self):
        if not self.content:
            return str('')
        encoding = self.encoding
        if encoding is None:
            encoding = self.apparent_encoding
        if encoding.lower() == 'utf-8':
            encoding = 'utf-8-sig'

        text = None
        try:
            text = str(self.content, encoding=encoding, errors='replace')
        except (LookupError, TypeError):
            text = str(self.content, errors='replace')
        return text

    # modified version from https://github.com/psf/requests/blob/428f7a275914f60a8f1e76a7d69516d617433d30/requests/models.py#L894 # noqa
    # no fast utf?? decoding, rely on cchardet
    def json(self):
        """Returns the json-encoded content of a response"""
        return json.loads(self.text)

    @property
    def reason(self):
        """Returns response headers"""
        if not self._headers:
            self._parse_headers_raw()
        return self._reason

    @property
    def headers(self):
        """Returns response headers"""
        if not self._headers:
            self._parse_headers_raw()
        return self._headers

    # from https://github.com/Lispython/human_curl/blob/1bdda958c4bb57f73f2332bfef5026a44270b3c3/human_curl/core.py#L864
    @property
    def cookies(self):
        """Returns list of BaseCookie object
        All cookies in list are ``Cookie.Morsel`` instance
        :return self._cookies: cookies list
        """
        if not self._cookies:
            self._parse_cookies()
        return self._cookies

    # from https://github.com/Lispython/human_curl/blob/1bdda958c4bb57f73f2332bfef5026a44270b3c3/human_curl/core.py#L876
    @property
    def history(self):
        """Returns redirects history list
        :return: list of `Response` objects
        """
        if not self._history:
            self._parse_headers_raw()
        return self._history

    # from https://github.com/psf/requests/blob/428f7a275914f60a8f1e76a7d69516d617433d30/requests/models.py#L698
    @property
    def ok(self):
        """Returns True if :attr:`status_code` is less than 400, False if not.
        This attribute checks if the status code of the response is between
        400 and 600 to see if there was a client error or a server error. If
        the status code is between 200 and 400, this will return True. This
        is **not** a check to see if the response code is ``200 OK``.
        """
        try:
            self.raise_for_status()
        except exceptions.HTTPError:
            return False
        return True

    # from https://github.com/psf/requests/blob/428f7a275914f60a8f1e76a7d69516d617433d30/requests/models.py#L938
    def raise_for_status(self):
        """Raises stored :class:`HTTPError`, if one occurred."""

        http_error_msg = ''
        if isinstance(self.reason, bytes):
            # We attempt to decode utf-8 first because some servers
            # choose to localize their reason strings. If the string
            # isn't utf-8, we fall back to iso-8859-1 for all other
            # encodings. (See PR #3538)
            try:
                reason = self.reason.decode('utf-8')
            except UnicodeDecodeError:
                reason = self.reason.decode('iso-8859-1')
        else:
            reason = self.reason

        if 400 <= self.status_code < 500:
            http_error_msg = u'%s Client Error: %s for url: %s' % (self.status_code, reason, self.url)

        elif 500 <= self.status_code < 600:
            http_error_msg = u'%s Server Error: %s for url: %s' % (self.status_code, reason, self.url)

        if http_error_msg:
            raise exceptions.HTTPError(http_error_msg)

        return self

    def __repr__(self):
        return '<Response [%s]>' % (self.status_code)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
