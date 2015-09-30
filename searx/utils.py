import cStringIO
import csv
import os
import re
import collections

from babel.dates import format_date
from codecs import getincrementalencoder
from HTMLParser import HTMLParser
from random import choice

from searx.version import VERSION_STRING
from searx import settings
from searx import logger
from searx.plugins import plugins


logger = logger.getChild('utils')

ua_versions = ('33.0',
               '34.0',
               '35.0',
               '36.0',
               '37.0',
               '38.0',
               '39.0',
               '40.0')

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
                regex_parts.append(u'\W+{0}\W+'.format(re.escape(chunk)))
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
        self.queue = cStringIO.StringIO()
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
        self.writer.writerow(unicode_row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def get_themes(root):
    """Returns available themes list."""

    static_path = os.path.join(root, 'static')
    templates_path = os.path.join(root, 'templates')

    themes = os.listdir(os.path.join(static_path, 'themes'))
    return static_path, templates_path, themes


def get_static_files(base_path):
    base_path = os.path.join(base_path, 'static')
    static_files = set()
    base_path_length = len(base_path) + 1
    for directory, _, files in os.walk(base_path):
        for filename in files:
            f = os.path.join(directory[base_path_length:], filename)
            static_files.add(f)
    return static_files


def get_result_templates(base_path):
    base_path = os.path.join(base_path, 'templates')
    result_templates = set()
    base_path_length = len(base_path) + 1
    for directory, _, files in os.walk(base_path):
        if directory.endswith('result_templates'):
            for filename in files:
                f = os.path.join(directory[base_path_length:], filename)
                result_templates.add(f)
    return result_templates


def format_date_by_locale(date, locale_string):
    # strftime works only on dates after 1900

    if date.year <= 1900:
        return date.isoformat().split('T')[0]

    if locale_string == 'all':
        locale_string = settings['ui']['default_locale'] or 'en_US'

    return format_date(date, locale=locale_string)


def dict_subset(d, properties):
    result = {}
    for k in properties:
        if k in d:
            result[k] = d[k]
    return result


def prettify_url(url, max_length=74):
    if len(url) > max_length:
        chunk_len = max_length / 2 + 1
        return u'{0}[...]{1}'.format(url[:chunk_len], url[-chunk_len:])
    else:
        return url


# get element in list or default value
def list_get(a_list, index, default=None):
    if len(a_list) > index:
        return a_list[index]
    else:
        return default


def get_blocked_engines(engines, user_config):
    blocked_engine_strings = user_config.get('blocked_engines')
    blocked_engines = []

    if not blocked_engine_strings:
        return blocked_engines

    for engine_string in blocked_engine_strings:
        if engine_string.find('__') > -1:
            engine, category = engine_string.split('__', 1)
            if engine in engines and category in engines[engine].categories:
                blocked_engines.append((engine, category))
        elif engine_string in engines:
            for category in engines[engine_string].categories:
                blocked_engines.append((engine_string, category))

    return blocked_engines


def parse_form(fields, collection_fields=None):
    regular_fields = dict()
    collection_field_data = collections.defaultdict(set)
    if collection_fields is None:
        collection_fields = []

    for name, value in fields:
        if name.startswith("plugin_"):
            collection_field_data["plugins"].add(name[len("plugin_"):])
        elif "_" in name and name.split("_")[0] in collection_fields:
            value = "_".join(name.split("_")[1:])
            plural_field_name = collection_fields[name.split("_")[0]]
            collection_field_data[plural_field_name].add(value)
        else:
            regular_fields[name] = value

    collection_field_data["plugins"] = [
        plugin_id for plugin_id in collection_field_data[
            "plugins"] if any(plugin.id == plugin_id for plugin in plugins)]
    for plugin in plugins:
        if plugin.default_on:
            if plugin.id in collection_field_data["plugins"]:
                collection_field_data["disabled_plugins"].add(plugin.id)
            elif plugin.id not in collection_field_data["plugins"]:
                collection_field_data["allowed_plugins"].add(plugin.id)

    del collection_field_data["plugins"]

    # FIXME: should we actually ever serialize this?
    # collection_field_data["disabled_plugins"] = ",".join(collection_field_data["disabled_plugins"])
    # collection_field_data["allowed_plugins"] = ",".join(collection_field_data["allowed_plugins"])

    fields = regular_fields
    fields.update(collection_field_data)
    return fields
