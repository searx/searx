import csv
import hashlib
import hmac
import os
import re

from babel.dates import format_date
from codecs import getincrementalencoder
from imp import load_source
from os.path import splitext, join
from random import choice
import sys

from searx.version import VERSION_STRING
from searx.languages import language_codes
from searx import settings
from searx import logger

try:
    from cStringIO import StringIO
except:
    from io import StringIO

try:
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser

if sys.version_info[0] == 3:
    unichr = chr
    unicode = str

logger = logger.getChild('utils')

ua_versions = ('40.0',
               '41.0',
               '42.0',
               '43.0',
               '44.0',
               '45.0',
               '46.0',
               '47.0')

ua_os = ('Windows NT 6.3; WOW64',
         'X11; Linux x86_64',
         'X11; Linux x86')

ua = "Mozilla/5.0 ({os}; rv:{version}) Gecko/20100101 Firefox/{version}"

blocked_tags = ('script',
                'style')


def gen_useragent():
    # TODO
    return ua.format(os=choice(ua_os), version=choice(ua_versions))


def searx_useragent():
    return 'searx/{searx_version} {suffix}'.format(
           searx_version=VERSION_STRING,
           suffix=settings['outgoing'].get('useragent_suffix', ''))


def highlight_content(content, query):

    if not content:
        return None
    # ignoring html contents
    # TODO better html content detection
    if content.find('<') != -1:
        return content

    query = query.decode('utf-8')
    if content.lower().find(query.lower()) > -1:
        query_regex = u'({0})'.format(re.escape(query))
        content = re.sub(query_regex, '<span class="highlight">\\1</span>',
                         content, flags=re.I | re.U)
    else:
        regex_parts = []
        for chunk in query.split():
            if len(chunk) == 1:
                regex_parts.append(u'\\W+{0}\\W+'.format(re.escape(chunk)))
            else:
                regex_parts.append(u'{0}'.format(re.escape(chunk)))
        query_regex = u'({0})'.format('|'.join(regex_parts))
        content = re.sub(query_regex, '<span class="highlight">\\1</span>',
                         content, flags=re.I | re.U)

    return content


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
            raise Exception("invalid html")

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
        if number[0] in (u'x', u'X'):
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(unichr(codepoint))

    def handle_entityref(self, name):
        if not self.is_valid_tag():
            return
        # codepoint = htmlentitydefs.name2codepoint[name]
        # self.result.append(unichr(codepoint))
        self.result.append(name)

    def get_text(self):
        return u''.join(self.result).strip()


def html_to_text(html):
    html = html.replace('\n', ' ')
    html = ' '.join(html.split())
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = getincrementalencoder(encoding)()

    def writerow(self, row):
        unicode_row = []
        for col in row:
            if type(col) == str or type(col) == unicode:
                unicode_row.append(col.encode('utf-8').strip())
            else:
                unicode_row.append(col)
        self.writer.writerow([x.decode('utf-8') if hasattr(x, 'decode') else x for x in unicode_row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue().strip('\x00')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data.decode('utf-8'))
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def get_resources_directory(searx_directory, subdirectory, resources_directory):
    if not resources_directory:
        resources_directory = os.path.join(searx_directory, subdirectory)
    if not os.path.isdir(resources_directory):
        raise Exception(directory + " is not a directory")
    return resources_directory


def get_themes(templates_path):
    """Returns available themes list."""
    themes = os.listdir(templates_path)
    if '__common__' in themes:
        themes.remove('__common__')
    return themes


def get_static_files(static_path):
    static_files = set()
    static_path_length = len(static_path) + 1
    for directory, _, files in os.walk(static_path):
        for filename in files:
            f = os.path.join(directory[static_path_length:], filename)
            static_files.add(f)
    return static_files


def get_result_templates(templates_path):
    result_templates = set()
    templates_path_length = len(templates_path) + 1
    for directory, _, files in os.walk(templates_path):
        if directory.endswith('result_templates'):
            for filename in files:
                f = os.path.join(directory[templates_path_length:], filename)
                result_templates.add(f)
    return result_templates


def format_date_by_locale(date, locale_string):
    # strftime works only on dates after 1900

    if date.year <= 1900:
        return date.isoformat().split('T')[0]

    if locale_string == 'all':
        locale_string = settings['ui']['default_locale'] or 'en_US'

    # to avoid crashing if locale is not supported by babel
    try:
        formatted_date = format_date(date, locale=locale_string)
    except:
        formatted_date = format_date(date, "YYYY-MM-dd")

    return formatted_date


def dict_subset(d, properties):
    result = {}
    for k in properties:
        if k in d:
            result[k] = d[k]
    return result


def prettify_url(url, max_length=74):
    if len(url) > max_length:
        chunk_len = int(max_length / 2 + 1)
        return u'{0}[...]{1}'.format(url[:chunk_len], url[-chunk_len:])
    else:
        return url


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
    is_abbr = (len(lang) == 2)
    if is_abbr:
        for l in language_codes:
            if l[0][:2] == lang.lower():
                return (True, l[0][:2], l[3].lower())
        return False
    else:
        for l in language_codes:
            if l[1].lower() == lang.lower():
                return (True, l[0][:2], l[3].lower())
        return False


def load_module(filename, module_dir):
    modname = splitext(filename)[0]
    if modname in sys.modules:
        del sys.modules[modname]
    filepath = join(module_dir, filename)
    module = load_source(modname, filepath)
    module.name = modname
    return module


def new_hmac(secret_key, url):
    if sys.version_info[0] == 2:
        return hmac.new(bytes(secret_key), url, hashlib.sha256).hexdigest()
    else:
        return hmac.new(bytes(secret_key, 'utf-8'), url, hashlib.sha256).hexdigest()
