import requests


the_http_adapter = requests.adapters.HTTPAdapter(pool_connections=100)
the_https_adapter = requests.adapters.HTTPAdapter(pool_connections=100)


class SessionSinglePool(requests.Session):

    def __init__(self):
        global the_https_adapter, the_http_adapter
        super(SessionSinglePool, self).__init__()

        # reuse the same adapters
        self.adapters.clear()
        self.mount('https://', the_https_adapter)
        self.mount('http://', the_http_adapter)

    def close(self):
        """Call super, but clear adapters since there are managed globaly"""
        self.adapters.clear()
        super(SessionSinglePool, self).close()


def request(method, url, **kwargs):
    """same as requests/requests/api.py request(...) except it use SessionSinglePool"""
    session = SessionSinglePool()
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


def post(url, data=None,  **kwargs):
    return request('post', url, data=data, **kwargs)


def put(url, data=None, **kwargs):
    return request('put', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    return request('patch', url, data=data, **kwargs)


def delete(url, **kwargs):
    return request('delete', url, **kwargs)
