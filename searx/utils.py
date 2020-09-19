# -*- coding: utf-8 -*-
import os
import sys
import re
import json

from imp import load_source
from numbers import Number
from os.path import splitext, join
from io import open
from random import choice
from html.parser import HTMLParser
from lxml.etree import XPath
from babel.core import get_global

from searx import settings
from searx.version import VERSION_STRING
from searx.languages import language_codes
from searx import logger


logger = logger.getChild('utils')

blocked_tags = ('script',
                'style')

ecma_unescape4_re = re.compile(r'%u([0-9a-fA-F]{4})', re.UNICODE)
ecma_unescape2_re = re.compile(r'%([0-9a-fA-F]{2})', re.UNICODE)

useragents = json.loads(open(os.path.dirname(os.path.realpath(__file__))
                             + "/data/useragents.json", 'r', encoding='utf-8').read())

xpath_cache = dict()
lang_to_lc_cache = dict()


def searx_useragent():
    return 'searx/{searx_version} {suffix}'.format(
           searx_version=VERSION_STRING,
           suffix=settings['outgoing'].get('useragent_suffix', ''))


def gen_useragent(os=None):
    return str(useragents['ua'].format(os=os or choice(useragents['os']), version=choice(useragents['versions'])))


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


def html_to_text(html):
    html = html.replace('\n', ' ')
    html = ' '.join(html.split())
    s = HTMLTextExtractor()
    try:
        s.feed(html)
    except HTMLTextExtractorException:
        logger.debug("HTMLTextExtractor: invalid HTML\n%s", html)
    return s.get_text()


def dict_subset(d, properties):
    result = {}
    for k in properties:
        if k in d:
            result[k] = d[k]
    return result


# get element in list or default value
def list_get(a_list, index, default=None):
    if len(a_list) > index:
        return a_list[index]
    else:
        return default


def get_torrent_size(filesize, filesize_multiplier):
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
    if number_str.isdigit():
        return int(number_str)
    else:
        return 0


# convert a variable to integer or return 0 if it's not a number
def int_or_zero(num):
    if isinstance(num, list):
        if len(num) < 1:
            return 0
        num = num[0]
    return convert_str_to_int(num)


def is_valid_lang(lang):
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


# auxiliary function to match lang_code in lang_list
def _match_language(lang_code, lang_list=[], custom_aliases={}):
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


# get the language code from lang_list that best matches locale_code
def match_language(locale_code, lang_list=[], custom_aliases={}, fallback='en-US'):
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
    module = load_source(modname, filepath)
    module.name = modname
    return module


def to_string(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, Number):
        return str(obj)
    if hasattr(obj, '__str__'):
        return obj.__str__()
    if hasattr(obj, '__repr__'):
        return obj.__repr__()


def ecma_unescape(s):
    """
    python implementation of the unescape javascript function

    https://www.ecma-international.org/ecma-262/6.0/#sec-unescape-string
    https://developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Objets_globaux/unescape
    """
    # s = unicode(s)
    # "%u5409" becomes "吉"
    s = ecma_unescape4_re.sub(lambda e: chr(int(e.group(1), 16)), s)
    # "%20" becomes " ", "%F3" becomes "ó"
    s = ecma_unescape2_re.sub(lambda e: chr(int(e.group(1), 16)), s)
    return s


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
    result = xpath_cache.get(xpath_str, None)
    if result is None:
        result = XPath(xpath_str)
        xpath_cache[xpath_str] = result
    return result


def eval_xpath(element, xpath_str):
    xpath = get_xpath(xpath_str)
    return xpath(element)
