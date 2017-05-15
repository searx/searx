import json
import re
import os
import sys
import unicodedata

from datetime import datetime

if sys.version_info[0] == 3:
    unicode = str

categories = []
url = 'https://download.finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&s={query}=X'
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

    ammount, from_currency, to_currency = m.groups()
    ammount = float(ammount)
    from_currency = name_to_iso4217(from_currency.strip())
    to_currency = name_to_iso4217(to_currency.strip())

    q = (from_currency + to_currency).upper()

    params['url'] = url.format(query=q)
    params['ammount'] = ammount
    params['from'] = from_currency
    params['to'] = to_currency
    params['from_name'] = iso4217_to_name(from_currency, 'en')
    params['to_name'] = iso4217_to_name(to_currency, 'en')

    return params


def response(resp):
    results = []
    try:
        _, conversion_rate, _ = resp.text.split(',', 2)
        conversion_rate = float(conversion_rate)
    except:
        return results

    answer = '{0} {1} = {2} {3}, 1 {1} ({5}) = {4} {3} ({6})'.format(
        resp.search_params['ammount'],
        resp.search_params['from'],
        resp.search_params['ammount'] * conversion_rate,
        resp.search_params['to'],
        conversion_rate,
        resp.search_params['from_name'],
        resp.search_params['to_name'],
    )

    now_date = datetime.now().strftime('%Y%m%d')
    url = 'https://finance.yahoo.com/currency/converter-results/{0}/{1}-{2}-to-{3}.html'  # noqa
    url = url.format(
        now_date,
        resp.search_params['ammount'],
        resp.search_params['from'].lower(),
        resp.search_params['to'].lower()
    )

    results.append({'answer': answer, 'url': url})

    return results


def load():
    global db

    current_dir = os.path.dirname(os.path.realpath(__file__))
    json_data = open(current_dir + "/../data/currencies.json").read()

    db = json.loads(json_data)


load()
