from sys import version_info

if version_info[0] == 2:
    from urllib import quote, quote_plus, unquote, urlencode
    from urlparse import parse_qsl, urljoin, urlparse, urlunparse, ParseResult
else:
    from urllib.parse import (
        parse_qsl,
        quote,
        quote_plus,
        unquote,
        urlencode,
        urljoin,
        urlparse,
        urlunparse,
        ParseResult
    )


__export__ = (parse_qsl,
              quote,
              quote_plus,
              unquote,
              urlencode,
              urljoin,
              urlparse,
              urlunparse,
              ParseResult)
