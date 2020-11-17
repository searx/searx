# -*- coding: utf-8 -*-
import sys
import re
import importlib

from numbers import Number
from os.path import splitext, join
from random import choice
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

from lxml import html
from lxml.etree import XPath, _ElementStringResult, _ElementUnicodeResult
from babel.core import get_global


from searx import settings
from searx.data import USER_AGENTS
from searx.version import VERSION_STRING
from searx.languages import language_codes
from searx import logger


logger = logger.getChild('utils')

blocked_tags = ('script',
                'style')

ecma_unescape4_re = re.compile(r'%u([0-9a-fA-F]{4})', re.UNICODE)
ecma_unescape2_re = re.compile(r'%([0-9a-fA-F]{2})', re.UNICODE)

xpath_cache = dict()
lang_to_lc_cache = dict()


def searx_useragent():
    """Return the searx User Agent"""
    return 'searx/{searx_version} {suffix}'.format(
           searx_version=VERSION_STRING,
           suffix=settings['outgoing'].get('useragent_suffix', ''))


def gen_useragent(os=None):
    """Return a random browser User Agent

    See searx/data/useragents.json
    """
    return str(USER_AGENTS['ua'].format(os=os or choice(USER_AGENTS['os']), version=choice(USER_AGENTS['versions'])))


class HTMLTextExtractorException(Exception):
    pass


class HTMLTextExtractor(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)

    def handle_endtag(self, tag):
        if not self.tags:
            return

        if tag != self.tags[-1]:
            raise HTMLTextExtractorException()

        self.tags.pop()

    def is_valid_tag(self):
        return not self.tags or self.tags[-1] not in blocked_tags

    def handle_data(self, d):
        if not self.is_valid_tag():
            return
        self.result.append(d)

    def handle_charref(self, number):
        if not self.is_valid_tag():
            return
        if number[0] in ('x', 'X'):
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def handle_entityref(self, name):
        if not self.is_valid_tag():
            return
        # codepoint = htmlentitydefs.name2codepoint[name]
        # self.result.append(chr(codepoint))
        self.result.append(name)

    def get_text(self):
        return ''.join(self.result).strip()


def html_to_text(html_str):
    """Extract text from a HTML string

    Args:
        * html_str (str): string HTML

    Returns:
        * str: extracted text

    Examples:
        >>> html_to_text('Example <span id="42">#2</span>')
        'Example #2'

        >>> html_to_text('<style>.span { color: red; }</style><span>Example</span>')
        'Example'
    """
    html_str = html_str.replace('\n', ' ')
    html_str = ' '.join(html_str.split())
    s = HTMLTextExtractor()
    try:
        s.feed(html_str)
    except HTMLTextExtractorException:
        logger.debug("HTMLTextExtractor: invalid HTML\n%s", html_str)
    return s.get_text()


def extract_text(xpath_results):
    """Extract text from a lxml result

      * if xpath_results is list, extract the text from each result and concat the list
      * if xpath_results is a xml element, extract all the text node from it
        ( text_content() method from lxml )
      * if xpath_results is a string element, then it's already done
    """
    if type(xpath_results) == list:
        # it's list of result : concat everything using recursive call
        result = ''
        for e in xpath_results:
            result = result + extract_text(e)
        return result.strip()
    elif type(xpath_results) in [_ElementStringResult, _ElementUnicodeResult]:
        # it's a string
        return ''.join(xpath_results)
    else:
        # it's a element
        text = html.tostring(
            xpath_results, encoding='unicode', method='text', with_tail=False
        )
        text = text.strip().replace('\n', ' ')
        return ' '.join(text.split())


def normalize_url(url, base_url):
    """Normalize URL: add protocol, join URL with base_url, add trailing slash if there is no path

    Args:
        * url (str): Relative URL
        * base_url (str): Base URL, it must be an absolute URL.

    Example:
        >>> normalize_url('https://example.com', 'http://example.com/')
        'https://example.com/'
        >>> normalize_url('//example.com', 'http://example.com/')
        'http://example.com/'
        >>> normalize_url('//example.com', 'https://example.com/')
        'https://example.com/'
        >>> normalize_url('/path?a=1', 'https://example.com')
        'https://example.com/path?a=1'
        >>> normalize_url('', 'https://example.com')
        'https://example.com/'
        >>> normalize_url('/test', '/path')
        raise Exception

    Raises:
        * lxml.etree.ParserError

    Returns:
        * str: normalized URL
    """
    if url.startswith('//'):
        # add http or https to this kind of url //example.com/
        parsed_search_url = urlparse(base_url)
        url = '{0}:{1}'.format(parsed_search_url.scheme or 'http', url)
    elif url.startswith('/'):
        # fix relative url to the search engine
        url = urljoin(base_url, url)

    # fix relative urls that fall through the crack
    if '://' not in url:
        url = urljoin(base_url, url)

    parsed_url = urlparse(url)

    # add a / at this end of the url if there is no path
    if not parsed_url.netloc:
        raise Exception('Cannot parse url')
    if not parsed_url.path:
        url += '/'

    return url


def extract_url(xpath_results, base_url):
    """Extract and normalize URL from lxml Element

    Args:
        * xpath_results (Union[List[html.HtmlElement], html.HtmlElement]): lxml Element(s)
        * base_url (str): Base URL

    Example:
        >>> def f(s, search_url):
        >>>    return searx.utils.extract_url(html.fromstring(s), search_url)
        >>> f('<span id="42">https://example.com</span>', 'http://example.com/')
        'https://example.com/'
        >>> f('https://example.com', 'http://example.com/')
        'https://example.com/'
        >>> f('//example.com', 'http://example.com/')
        'http://example.com/'
        >>> f('//example.com', 'https://example.com/')
        'https://example.com/'
        >>> f('/path?a=1', 'https://example.com')
        'https://example.com/path?a=1'
        >>> f('', 'https://example.com')
        raise lxml.etree.ParserError
        >>> searx.utils.extract_url([], 'https://example.com')
        raise Exception

    Raises:
        * Exception
        * lxml.etree.ParserError

    Returns:
        * str: normalized URL
    """
    if xpath_results == []:
        raise Exception('Empty url resultset')

    url = extract_text(xpath_results)
    return normalize_url(url, base_url)


def dict_subset(d, properties):
    """Extract a subset of a dict

    Examples:
        >>> dict_subset({'A': 'a', 'B': 'b', 'C': 'c'}, ['A', 'C'])
        {'A': 'a', 'C': 'c'}
        >>> >> dict_subset({'A': 'a', 'B': 'b', 'C': 'c'}, ['A', 'D'])
        {'A': 'a'}
    """
    result = {}
    for k in properties:
        if k in d:
            result[k] = d[k]
    return result


def list_get(a_list, index, default=None):
    """Get element in list or default value

    Examples:
        >>> list_get(['A', 'B', 'C'], 0)
        'A'
        >>> list_get(['A', 'B', 'C'], 3)
        None
        >>> list_get(['A', 'B', 'C'], 3, 'default')
        'default'
        >>> list_get(['A', 'B', 'C'], -1)
        'C'
    """
    if len(a_list) > index:
        return a_list[index]
    else:
        return default


def get_torrent_size(filesize, filesize_multiplier):
    """

    Args:
        * filesize (str): size
        * filesize_multiplier (str): TB, GB, .... TiB, GiB...

    Returns:
        * int: number of bytes

    Example:
        >>> get_torrent_size('5', 'GB')
        5368709120
        >>> get_torrent_size('3.14', 'MiB')
        3140000
    """
    try:
        filesize = float(filesize)

        if filesize_multiplier == 'TB':
            filesize = int(filesize * 1024 * 1024 * 1024 * 1024)
        elif filesize_multiplier == 'GB':
            filesize = int(filesize * 1024 * 1024 * 1024)
        elif filesize_multiplier == 'MB':
            filesize = int(filesize * 1024 * 1024)
        elif filesize_multiplier == 'KB':
            filesize = int(filesize * 1024)
        elif filesize_multiplier == 'TiB':
            filesize = int(filesize * 1000 * 1000 * 1000 * 1000)
        elif filesize_multiplier == 'GiB':
            filesize = int(filesize * 1000 * 1000 * 1000)
        elif filesize_multiplier == 'MiB':
            filesize = int(filesize * 1000 * 1000)
        elif filesize_multiplier == 'KiB':
            filesize = int(filesize * 1000)
    except:
        filesize = None

    return filesize


def convert_str_to_int(number_str):
    """Convert number_str to int or 0 if number_str is not a number."""
    if number_str.isdigit():
        return int(number_str)
    else:
        return 0


def int_or_zero(num):
    """Convert num to int or 0. num can be either a str or a list.
    If num is a list, the first element is converted to int (or return 0 if the list is empty).
    If num is a str, see convert_str_to_int
    """
    if isinstance(num, list):
        if len(num) < 1:
            return 0
        num = num[0]
    return convert_str_to_int(num)


def is_valid_lang(lang):
    """Return language code and name if lang describe a language.

    Examples:
        >>> is_valid_lang('zz')
        False
        >>> is_valid_lang('uk')
        (True, 'uk', 'ukrainian')
        >>> is_valid_lang(b'uk')
        (True, 'uk', 'ukrainian')
        >>> is_valid_lang('en')
        (True, 'en', 'english')
        >>> searx.utils.is_valid_lang('Español')
        (True, 'es', 'spanish')
        >>> searx.utils.is_valid_lang('Spanish')
        (True, 'es', 'spanish')
    """
    if isinstance(lang, bytes):
        lang = lang.decode()
    is_abbr = (len(lang) == 2)
    lang = lang.lower()
    if is_abbr:
        for l in language_codes:
            if l[0][:2] == lang:
                return (True, l[0][:2], l[3].lower())
        return False
    else:
        for l in language_codes:
            if l[1].lower() == lang or l[3].lower() == lang:
                return (True, l[0][:2], l[3].lower())
        return False


def _get_lang_to_lc_dict(lang_list):
    key = str(lang_list)
    value = lang_to_lc_cache.get(key, None)
    if value is None:
        value = dict()
        for lc in lang_list:
            value.setdefault(lc.split('-')[0], lc)
        lang_to_lc_cache[key] = value
    return value


def _match_language(lang_code, lang_list=[], custom_aliases={}):
    """auxiliary function to match lang_code in lang_list"""
    # replace language code with a custom alias if necessary
    if lang_code in custom_aliases:
        lang_code = custom_aliases[lang_code]

    if lang_code in lang_list:
        return lang_code

    # try to get the most likely country for this language
    subtags = get_global('likely_subtags').get(lang_code)
    if subtags:
        subtag_parts = subtags.split('_')
        new_code = subtag_parts[0] + '-' + subtag_parts[-1]
        if new_code in custom_aliases:
            new_code = custom_aliases[new_code]
        if new_code in lang_list:
            return new_code

    # try to get the any supported country for this language
    return _get_lang_to_lc_dict(lang_list).get(lang_code, None)


def match_language(locale_code, lang_list=[], custom_aliases={}, fallback='en-US'):
    """get the language code from lang_list that best matches locale_code"""
    # try to get language from given locale_code
    language = _match_language(locale_code, lang_list, custom_aliases)
    if language:
        return language

    locale_parts = locale_code.split('-')
    lang_code = locale_parts[0]

    # try to get language using an equivalent country code
    if len(locale_parts) > 1:
        country_alias = get_global('territory_aliases').get(locale_parts[-1])
        if country_alias:
            language = _match_language(lang_code + '-' + country_alias[0], lang_list, custom_aliases)
            if language:
                return language

    # try to get language using an equivalent language code
    alias = get_global('language_aliases').get(lang_code)
    if alias:
        language = _match_language(alias, lang_list, custom_aliases)
        if language:
            return language

    if lang_code != locale_code:
        # try to get language from given language without giving the country
        language = _match_language(lang_code, lang_list, custom_aliases)

    return language or fallback


def load_module(filename, module_dir):
    modname = splitext(filename)[0]
    if modname in sys.modules:
        del sys.modules[modname]
    filepath = join(module_dir, filename)
    # and https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    spec = importlib.util.spec_from_file_location(modname, filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    spec.loader.exec_module(module)
    return module


def to_string(obj):
    """Convert obj to its string representation."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, Number):
        return str(obj)
    if hasattr(obj, '__str__'):
        return obj.__str__()
    if hasattr(obj, '__repr__'):
        return obj.__repr__()


def ecma_unescape(s):
    """Python implementation of the unescape javascript function

    https://www.ecma-international.org/ecma-262/6.0/#sec-unescape-string
    https://developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Objets_globaux/unescape

    Examples:
        >>> ecma_unescape('%u5409')
        '吉'
        >>> ecma_unescape('%20')
        ' '
        >>> ecma_unescape('%F3')
        'ó'
    """
    # "%u5409" becomes "吉"
    s = ecma_unescape4_re.sub(lambda e: chr(int(e.group(1), 16)), s)
    # "%20" becomes " ", "%F3" becomes "ó"
    s = ecma_unescape2_re.sub(lambda e: chr(int(e.group(1), 16)), s)
    return s


def get_string_replaces_function(replaces):
    rep = {re.escape(k): v for k, v in replaces.items()}
    pattern = re.compile("|".join(rep.keys()))

    def f(text):
        return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

    return f


def get_engine_from_settings(name):
    """Return engine configuration from settings.yml of a given engine name"""

    if 'engines' not in settings:
        return {}

    for engine in settings['engines']:
        if 'name' not in engine:
            continue
        if name == engine['name']:
            return engine

    return {}


def get_xpath(xpath_str):
    """Return cached compiled XPath

    There is no thread lock.
    Worst case scenario, xpath_str is compiled more than one time.
    """
    result = xpath_cache.get(xpath_str, None)
    if result is None:
        result = XPath(xpath_str)
        xpath_cache[xpath_str] = result
    return result


def eval_xpath(element, xpath_str):
    """Equivalent of element.xpath(xpath_str) but compile xpath_str once for all."""
    xpath = get_xpath(xpath_str)
    return xpath(element)
