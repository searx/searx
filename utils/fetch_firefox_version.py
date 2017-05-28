#!/usr/bin/env python

# set path
from sys import path
from os.path import realpath, dirname
path.append(realpath(dirname(realpath(__file__)) + '/../'))

#
import json
import requests
import re
from distutils.version import LooseVersion, StrictVersion
from lxml import html
from searx.url_utils import urlparse, urljoin

URL = 'https://ftp.mozilla.org/pub/firefox/releases/'
RELEASE_PATH = '/pub/firefox/releases/'

NORMAL_REGEX = re.compile('^[0-9]+\.[0-9](\.[0-9])?(esr)?$')
# BETA_REGEX = re.compile('.*[0-9]b([0-9\-a-z]+)$')
# ESR_REGEX = re.compile('^[0-9]+\.[0-9](\.[0-9])?esr$')

# 
useragent = {
    "versions": (),
    "os": ('Windows NT 10; WOW64',
           'X11; Linux x86_64'),
    "ua": "Mozilla/5.0 ({os}; rv:{version}) Gecko/20100101 Firefox/{version}"
}


def fetch_firefox_versions():
    resp = requests.get(URL, timeout=2.0)
    if resp.status_code != 200:
        raise Exception("Error fetching firefox versions, HTTP code " + resp.status_code)
    else:
        dom = html.fromstring(resp.text)
        versions = []

        for link in dom.xpath('//a/@href'):
            url = urlparse(urljoin(URL, link))
            path = url.path
            if path.startswith(RELEASE_PATH):
                version = path[len(RELEASE_PATH):-1]
                if NORMAL_REGEX.match(version):
                    versions.append(LooseVersion(version))

        list.sort(versions, reverse=True)
        return versions


def fetch_firefox_last_versions():
    versions = fetch_firefox_versions()

    result = []
    major_last = versions[0].version[0]
    major_list = (major_last, major_last - 1)
    for version in versions:
        major_current = version.version[0]
        if major_current in major_list and 'esr' not in version.version:
            result.append(version.vstring)

    return result


useragent["versions"] = fetch_firefox_last_versions()
f = open("../searx/data/useragents.json", "wb")
json.dump(useragent, f, sort_keys=True, indent=4, ensure_ascii=False, encoding="utf-8")
f.close()
