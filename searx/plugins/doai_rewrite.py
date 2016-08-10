from flask_babel import gettext
import re
from urlparse import urlparse, parse_qsl

regex = re.compile(r'10\.\d{4,9}/[^\s]+')

name = gettext('DOAI rewrite')
description = gettext('Avoid paywalls by redirecting to open-access versions of publications when available')
default_on = False


def extract_doi(url):
    match = regex.search(url.path)
    if match:
        return match.group(0)
    for _, v in parse_qsl(url.query):
        match = regex.search(v)
        if match:
            return match.group(0)
    return None


def on_result(request, ctx):
    doi = extract_doi(ctx['result']['parsed_url'])
    if doi and len(doi) < 50:
        for suffix in ('/', '.pdf', '/full', '/meta', '/abstract'):
            if doi.endswith(suffix):
                doi = doi[:-len(suffix)]
        ctx['result']['url'] = 'http://doai.io/' + doi
        ctx['result']['parsed_url'] = urlparse(ctx['result']['url'])
    return True
