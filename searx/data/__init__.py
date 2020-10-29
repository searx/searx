import json
from pathlib import Path


__init__ = ['ENGINES_LANGUGAGES', 'CURRENCIES', 'USER_AGENTS', 'EXTERNAL_URLS', 'WIKIDATA_UNITS',
            'bangs_loader', 'ahmia_blacklist_loader']
data_dir = Path(__file__).parent


def load(filename):
    # add str(...) for Python 3.5
    with open(str(data_dir / filename), encoding='utf-8') as fd:
        return json.load(fd)


def bangs_loader():
    return load('bangs.json')


def ahmia_blacklist_loader():
    with open(str(data_dir / 'ahmia_blacklist.txt'), encoding='utf-8') as fd:
        return fd.read().split()


ENGINES_LANGUAGES = load('engines_languages.json')
CURRENCIES = load('currencies.json')
USER_AGENTS = load('useragents.json')
EXTERNAL_URLS = load('external_urls.json')
WIKIDATA_UNITS = load('wikidata_units.json')
