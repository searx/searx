# -*- coding: utf-8 -*-
import os
import csv
import hashlib
import hmac
import re
import inspect

from io import StringIO
from codecs import getincrementalencoder

from searx import logger


VALID_LANGUAGE_CODE = re.compile(r'^[a-z]{2,3}(-[a-zA-Z]{2})?$')

logger = logger.getChild('webutils')


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
        self.writer.writerow(row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.strip('\x00')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data.decode())
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def new_hmac(secret_key, url):
    try:
        secret_key_bytes = bytes(secret_key, 'utf-8')
    except TypeError as err:
        if isinstance(secret_key, bytes):
            secret_key_bytes = secret_key
        else:
            raise err
    return hmac.new(secret_key_bytes, url, hashlib.sha256).hexdigest()


def prettify_url(url, max_length=74):
    if len(url) > max_length:
        chunk_len = int(max_length / 2 + 1)
        return '{0}[...]{1}'.format(url[:chunk_len], url[-chunk_len:])
    else:
        return url


def highlight_content(content, query):

    if not content:
        return None
    # ignoring html contents
    # TODO better html content detection
    if content.find('<') != -1:
        return content

    if content.lower().find(query.lower()) > -1:
        query_regex = '({0})'.format(re.escape(query))
        content = re.sub(query_regex, '<span class="highlight">\\1</span>',
                         content, flags=re.I | re.U)
    else:
        regex_parts = []
        for chunk in query.split():
            if len(chunk) == 1:
                regex_parts.append('\\W+{0}\\W+'.format(re.escape(chunk)))
            else:
                regex_parts.append('{0}'.format(re.escape(chunk)))
        query_regex = '({0})'.format('|'.join(regex_parts))
        content = re.sub(query_regex, '<span class="highlight">\\1</span>',
                         content, flags=re.I | re.U)

    return content


def is_flask_run_cmdline():
    """Check if the application was started using "flask run" command line

    Inspect the callstack.
    See https://github.com/pallets/flask/blob/master/src/flask/__main__.py

    Returns:
        bool: True if the application was started using "flask run".
    """
    frames = inspect.stack()
    if len(frames) < 2:
        return False
    return frames[-2].filename.endswith('flask/cli.py')
