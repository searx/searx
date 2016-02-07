import logging
import pycurl
import threading
from itertools import cycle
from StringIO import StringIO
from time import time
from urllib import urlencode


CURL_SHARE = pycurl.CurlShare()
CURL_SHARE.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_DNS)
MULTI_HANDLER = pycurl.CurlMulti()


def __test_callback(*args):
    print "callback called"


def get_connection(source_address=None):
    # pycurl initialization
    h = pycurl.Curl()

    # follow redirects
    h.setopt(h.FOLLOWLOCATION, True)

    # consistently use ipv4
    h.setopt(h.IPRESOLVE, pycurl.IPRESOLVE_V4)

    h.setopt(pycurl.SHARE, CURL_SHARE)

    if source_address:
        h.setopt(h.INTERFACE, source_address)

    return h


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
        curl_handler.setopt(curl_handler.SSL_VERIFYPEER, int(ssl_verification))

    def _extract_response(self):
        body = self._response_buffer.getvalue()
        status_code = self.curl_handler.getinfo(pycurl.HTTP_CODE)
        return ResponseContainer(body, status_code, self.url)

    def finish(self):
        self.response = self._extract_response()
        if self.callback:
            return self.callback(self.response)


class ResponseContainer(object):
    def __init__(self, body, status_code, url):
        self.text = self.content = body
        self.status_code = status_code
        self.url = url


class MultiRequest(object):
    def __init__(self, multi_handler=None, source_ips=None):
        self.requests = {}

        if multi_handler:
            self._curl_multi_handler = multi_handler
        else:
            self._curl_multi_handler = MULTI_HANDLER

        self.source_ips = cycle(source_ips) if source_ips else cycle([None])

    def add(self, url, **kwargs):
        handle = get_connection(next(self.source_ips))
        request_container = RequestContainer(url, handle, **kwargs)
        try:
            self._curl_multi_handler.add_handle(handle)
        except:
            print 'meep'
            pass
        self.requests[handle] = request_container

    def send_requests(self):
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

        search_start = time()
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
                        th = threading.Thread(
                            target=self.requests[h].finish(),
                            name='search_request',
                        )
                        th.start()
                        # self.requests[h].finish()
                    for h, err_code, err_string in error_list:
                        logging.warn('Error on %s: "%s"', self.requests[h].url, err_string)
                    handles_num -= len(success_list) + len(error_list)
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break

        for th in threading.enumerate():
            if th.name == 'search_request':
                remaining_time = max(0.0, timeout - (time() - search_start))
                th.join(remaining_time)
                if th.isAlive():
                    logging.warning('engine timeout: {0}'.format(th._engine_name))

        # self._curl_multi_handler.close()
        return self.requests.values()


if __name__ == '__main__':
    r = MultiRequest()
    r.add('http://httpbin.org/delay/0', headers={'User-Agent': 'x'})
    r.add('http://127.0.0.1:7777/', headers={'User-Agent': 'x'})
    r.add('http://httpbin.org/delay/0', cookies={'as': 'sa', 'bb': 'cc'})
    r.add('http://httpbin.org/delay/0', callback=__test_callback, timeout=1.0, headers={'User-Agent': 'x'})
    for v in r.send_requests():
        print v.url
        print v.response.text
