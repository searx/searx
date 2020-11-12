import hmac
import hashlib
from urllib.parse import urlencode

from searx.webutils import new_hmac
from searx import settings


def add_protocol(url):
    if url.startswith('//'):
        return 'https:' + url
    return url


def proxify(url):
    url = add_protocol(url)

    if not settings.get('result_proxy'):
        return url

    url_params = dict(mortyurl=url.encode())

    if settings['result_proxy'].get('key'):
        url_params['mortyhash'] = hmac.new(settings['result_proxy']['key'],
                                           url.encode(),
                                           hashlib.sha256).hexdigest()

    return '{0}?{1}'.format(settings['result_proxy']['url'],
                            urlencode(url_params))


def image_proxify(image_proxy_url, url):
    url = add_protocol(url)

    if url.startswith('data:image/'):
        # 50 is an arbitrary number to get only the beginning of the image.
        partial_base64 = url[len('data:image/'):50].split(';')
        if len(partial_base64) == 2 \
           and partial_base64[0] in ['gif', 'png', 'jpeg', 'pjpeg', 'webp', 'tiff', 'bmp']\
           and partial_base64[1].startswith('base64,'):
            return url
        else:
            return None

    if settings.get('result_proxy'):
        return proxify(url)

    h = new_hmac(settings['server']['secret_key'], url.encode())

    return '{0}?{1}'.format(image_proxy_url,
                            urlencode(dict(url=url.encode(), h=h)))


def check_hmac_for_url(url, h):
    return h != new_hmac(settings['server']['secret_key'], url)
