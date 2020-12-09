import json
import re
import unicodedata
from searx.data import CURRENCIES  # NOQA


categories = []
url = 'https://duckduckgo.com/js/spice/currency/1/{0}/{1}'
weight = 100

parser_re = re.compile('.*?(\\d+(?:\\.\\d+)?) ([^.0-9]+) (?:in|to) ([^.0-9]+)', re.I)
https_support = True


def normalize_name(name):
    name = name.lower().replace('-', ' ').rstrip('s')
    name = re.sub(' +', ' ', name)
    return unicodedata.normalize('NFKD', name).lower()


def name_to_iso4217(name):
    global CURRENCIES

    name = normalize_name(name)
    currency = CURRENCIES['names'].get(name, [name])
    return currency[0]


def iso4217_to_name(iso4217, language):
    global CURRENCIES

    return CURRENCIES['iso4217'].get(iso4217, {}).get(language, iso4217)


def request(query, params):
    m = parser_re.match(query)
    if not m:
        # wrong query
        return params
    amount, from_currency, to_currency = m.groups()
    amount = float(amount)
    from_currency = name_to_iso4217(from_currency.strip())
    to_currency = name_to_iso4217(to_currency.strip())

    params['url'] = url.format(from_currency, to_currency)
    params['amount'] = amount
    params['from'] = from_currency
    params['to'] = to_currency
    params['from_name'] = iso4217_to_name(from_currency, 'en')
    params['to_name'] = iso4217_to_name(to_currency, 'en')

    return params


def response(resp):
    """remove first and last lines to get only json"""
    json_resp = resp.text[resp.text.find('\n') + 1:resp.text.rfind('\n') - 2]
    results = []
    try:
        conversion_rate = float(json.loads(json_resp)['conversion']['converted-amount'])
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

    url = 'https://duckduckgo.com/js/spice/currency/1/{0}/{1}'.format(
        resp.search_params['from'].upper(), resp.search_params['to'])

    results.append({'answer': answer, 'url': url})

    return results
