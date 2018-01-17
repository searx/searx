import json
import re
import os
import sys
import unicodedata

from io import open
from datetime import datetime

if sys.version_info[0] == 3:
    unicode = str

categories = []
url = 'https://finance.google.com/finance/converter?a=1&from={0}&to={1}'
weight = 100

parser_re = re.compile(b'.*?(\\d+(?:\\.\\d+)?) ([^.0-9]+) (?:in|to) ([^.0-9]+)', re.I)

db = 1


def normalize_name(name):
    name = name.decode('utf-8').lower().replace('-', ' ').rstrip('s')
    name = re.sub(' +', ' ', name)
    return unicodedata.normalize('NFKD', name).lower()


def name_to_iso4217(name):
    global db

    name = normalize_name(name)
    currencies = db['names'].get(name, [name])
    return currencies[0]


def iso4217_to_name(iso4217, language):
    global db

    return db['iso4217'].get(iso4217, {}).get(language, iso4217)


def request(query, params):
    m = parser_re.match(query)
    if not m:
        # wrong query
        return params

    amount, from_currency, to_currency = m.groups()
    amount = float(amount)
    from_currency = name_to_iso4217(from_currency.strip())
    to_currency = name_to_iso4217(to_currency.strip())

    q = (from_currency + to_currency).upper()

    params['url'] = url.format(from_currency, to_currency)
    params['amount'] = amount
    params['from'] = from_currency
    params['to'] = to_currency
    params['from_name'] = iso4217_to_name(from_currency, 'en')
    params['to_name'] = iso4217_to_name(to_currency, 'en')

    return params


def response(resp):
    results = []
    pat = '<span class=bld>(.+) {0}</span>'.format(
        resp.search_params['to'].upper())

    try:
        conversion_rate = re.findall(pat, resp.text)[0]
        conversion_rate = float(conversion_rate)
    except:
        return results

    answer = '{0} {1} = {2} {3}, 1 {1} ({5}) = {4} {3} ({6})'.format(
        resp.search_params['amount'],
        resp.search_params['from'],
        resp.search_params['amount'] * conversion_rate,
        resp.search_params['to'],
        conversion_rate,
        resp.search_params['from_name'],
        resp.search_params['to_name'],
    )

    url = 'https://finance.google.com/finance?q={0}{1}'.format(
        resp.search_params['from'].upper(), resp.search_params['to'])

    results.append({'answer': answer, 'url': url})

    return results


def load():
    global db

    current_dir = os.path.dirname(os.path.realpath(__file__))
    json_data = open(current_dir + "/../data/currencies.json", 'r', encoding='utf-8').read()

    db = json.loads(json_data)


load()
