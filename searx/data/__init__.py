import json
from pathlib import Path


__init__ = ['ENGINES_LANGUGAGES', 'CURRENCIES', 'USER_AGENTS', 'bangs_loader']
data_dir = Path(__file__).parent


def load(filename):
    # add str(...) for Python 3.5
    with open(str(data_dir / filename), encoding='utf-8') as fd:
        return json.load(fd)


def bangs_loader():
    return load('bangs.json')


ENGINES_LANGUAGES = load('engines_languages.json')
CURRENCIES = load('currencies.json')
USER_AGENTS = load('useragents.json')
