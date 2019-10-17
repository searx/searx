import distro
import pycurl
from searx.httpclient.utils import logger

try:
    import platform
    if platform.system().lower() != 'windows':
        import signal
        from threading import current_thread
        if current_thread().name == 'MainThread':
            signal.signal(signal.SIGPIPE, signal.SIG_IGN)
except ImportError:
    pass


def enable_http2():
    d = distro.linux_distribution(full_distribution_name=False)
    if d[0] == 'ubuntu' and d[1] == '18.04':
        """
        libcurl from Ubuntu 18.04.3 LTS segfaults on heavy load when HTTP/2 is used:
        #0  Curl_add_buffer (in=0x0, inptr=inptr@entry=0x7f7d7023c108, size=size@entry=7) at http.c:1227
        #1  0x00007f7d7021d67e in on_header (session=<optimized out>, frame=0x7f7d64512c68, name=<optimized out>, namelen=7, value=0x7f7d6ffc53bd "404", valuelen=3, flags=0 '\000', userp=0x7f7d642169d0) at http2.c:951
        #2  0x00007f7d6ffbbc62 in nghttp2_session_mem_recv () from /usr/lib/x86_64-linux-gnu/libnghttp2.so.14
        #3  0x00007f7d7021f186 in http2_recv (conn=0x7f7d642169d0, sockindex=<optimized out>, mem=0x3728060 "", len=<optimized out>, err=0x7f7d68e241c4) at http2.c:1581
        #4  0x00007f7d701e932d in Curl_read (conn=conn@entry=0x7f7d642169d0, sockfd=17, buf=0x3728060 "", sizerequested=16384, n=n@entry=0x7f7d68e24270) at sendf.c:741
        #5  0x00007f7d701fb619 in readwrite_data (comeback=0x7f7d68e242fb, done=0x7f7d68e242f9, didwhat=<synthetic pointer>, k=0x3722e30, conn=0x7f7d642169d0, data=0x3722d70) at transfer.c:475
        #6  Curl_readwrite (conn=0x7f7d642169d0, data=data@entry=0x3722d70, done=done@entry=0x7f7d68e242f9, comeback=comeback@entry=0x7f7d68e242fb) at transfer.c:1118
        #7  0x00007f7d70205e8b in multi_runsingle (multi=multi@entry=0x110c7c0, now=..., data=data@entry=0x3722d70) at multi.c:1871
        #8  0x00007f7d702073e4 in curl_multi_perform (multi=0x110c7c0, running_handles=running_handles@entry=0x7f7d68e24474) at multi.c:2136

        may be this code misuses libcurl, maybe there is a real in libcurl 7.58.0
        doesn't happen with Alpine linux 3.10
        """  # noqa
        logger.warn('HTTP/2 disabled because of a bug in libcurl')
        return False

    features = PYCURL_VERSION[4]
    # hardcoded value to fail safe: pycurl.VERSION_HTTP2 == 65536
    return features & 65536 != 0


def curl_version_ge(major, minor, patch):
    v = (major << 16) | (minor << 8) | patch
    return PYCURL_VERSION[2] >= v


PYCURL_VERSION = pycurl.version_info()
HAS_HTTP2 = enable_http2()

pycurl.global_init(pycurl.GLOBAL_ALL)
