import pycurl
from StringIO import StringIO
from urllib import urlencode


def __test_callback(*args):
    print "callback called"


def get_new_connection(source_address=None):
    # pycurl initialization
    h = pycurl.Curl()

    # Do not follow redirect.
    h.setopt(h.FOLLOWLOCATION, False)

    # consistently use ipv4
    h.setopt(h.IPRESOLVE, pycurl.IPRESOLVE_V4)

    if source_address:
        h.setopt(h.INTERFACE, source_address)

    return h


class ConnectionSources(object):
    def __init__(self, sources=None):
        self.sources = []
        if sources:
            for s in sources:
                self.sources.append(get_new_connection(s))
        else:
            self.sources.append(get_new_connection())
        self.ptr = 0

    def get_source(self):
        source = self.sources[self.ptr]
        self.ptr = (self.ptr + 1) % len(self.sources)
        return source


class ConnectionCache(object):
    def __init__(self, source_ips=None):
        self.source_ips = source_ips if source_ips else None
        self.connections = {}

    def get_connection(self, key):
        if key in self.connections:
            return self.connections[key].get_source()

        sources = ConnectionSources(self.source_ips)
        self.connections[key] = sources
        return sources.get_source()


CONNECTION_CACHE = ConnectionCache()


class RequestContainer(object):
    def __init__(self,
                 url,
                 curl_handler,
                 method='GET',
                 headers=None,
                 cookies=None,
                 callback=None,
                 data=None,
                 timeout=2.0,
                 ssl_verification=True):

        if headers is None:
            headers = {}

        if cookies is None:
            cookies = {}

        if data is not None:
            curl_handler.setopt(curl_handler.POSTFIELDS, urlencode(data))

        self.url = url
        self.headers = headers
        self.cookies = cookies
        self.timeout = int(timeout * 1000)  # in milisecs
        self.callback = callback
        self.curl_handler = curl_handler

        self._response_buffer = StringIO()
        self.response = None
        curl_handler.setopt(curl_handler.WRITEFUNCTION, self._response_buffer.write)

    def _extract_response(self):
        body = self._response_buffer.getvalue()
        status = self.curl_handler.getinfo(pycurl.HTTP_CODE)
        return ResponseContainer(body, status, self.url)

    def finish(self):
        self.response = self._extract_response()
        if self.callback:
            return self.callback(self.response)


class ResponseContainer(object):
    def __init__(self, body, status, url):
        self.text = self.content = body
        self.status = status
        self.url = url


class MultiRequest(object):
    def __init__(self, connection_cache=None):
        self.requests = {}
        self._curl_multi_handler = pycurl.CurlMulti()

        if connection_cache:
            self.connection_cache = connection_cache
        else:
            self.connection_cache = CONNECTION_CACHE

    def add(self, connection_name, url, **kwargs):
        handle = self.connection_cache.get_connection(connection_name)
        request_container = RequestContainer(url, handle, **kwargs)
        self._curl_multi_handler.add_handle(handle)
        self.requests[handle] = request_container

    def perform_requests(self):
        select_timeout = 0.1

        # set timeout
        timeout = max(c.timeout for c in self.requests.values())
        for h, c in self.requests.iteritems():
            h.setopt(h.CONNECTTIMEOUT_MS, timeout)
            h.setopt(h.TIMEOUT_MS, timeout)
            h.setopt(h.URL, c.url)
            c.headers['Connection'] = 'keep-alive'
            # c.headers['Accept-Encoding'] = 'gzip, deflate'

            h.setopt(h.HTTPHEADER,
                     ['{0}: {1}'.format(k, v)
                      for k, v in c.headers.iteritems()])

            if c.cookies:
                h.setopt(h.COOKIE, '; '.join('{0}={1}'.format(k, v)
                                             for k, v in c.cookies.iteritems()))
            else:
                h.unsetopt(h.COOKIE)

        handles_num = len(self.requests)
        while handles_num:
            self._curl_multi_handler.select(select_timeout)
            while 1:
                ret, new_handles_num = self._curl_multi_handler.perform()
                # handle finished
                if new_handles_num < handles_num:
                    _, success_list, error_list = self._curl_multi_handler.info_read()
                    # calling callbacks
                    for h in success_list:
                        self.requests[h].finish()
                    handles_num -= len(success_list) + len(error_list)
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break

        # response arrived
        for k in self.requests:
            if k.errstr():
                print k.errstr()
                # TODO handle errors/timeouts
                pass
            self._curl_multi_handler.remove_handle(k)
        # self._curl_multi_handler.close()
        return self.requests.values()


if __name__ == '__main__':
    r = MultiRequest()
    r.add('a', 'http://httpbin.org/delay/0', headers={'User-Agent': 'x'})
    r.add('d', 'http://127.0.0.1:7777/', headers={'User-Agent': 'x'})
    r.add('b', 'http://httpbin.org/delay/0', cookies={'as': 'sa', 'bb': 'cc'})
    r.add('c', 'http://httpbin.org/delay/0', callback=__test_callback, timeout=1.0, headers={'User-Agent': 'x'})
    for v in r.perform_requests():
        print v.url
        print v.response.text
