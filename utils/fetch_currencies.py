# -*- coding: utf-8 -*-
import json
import re
import unicodedata
import string
from urllib import urlencode
from requests import get

languages = {'de', 'en', 'es', 'fr', 'hu', 'it', 'nl', 'jp'}

url_template = 'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&{query}&props=labels%7Cdatatype%7Cclaims%7Caliases&languages=' + '|'.join(languages)
url_wmflabs_template = 'http://wdq.wmflabs.org/api?q='
url_wikidata_search_template = 'http://www.wikidata.org/w/api.php?action=query&list=search&format=json&srnamespace=0&srprop=sectiontitle&{query}'

wmflabs_queries = [
    'CLAIM[31:8142]',  # all devise
]

db = {
    'iso4217': {
    },
    'names': {
    }
}


def remove_accents(data):
    return unicodedata.normalize('NFKD', data).lower()


def normalize_name(name):
    return re.sub(' +', ' ', remove_accents(name.lower()).replace('-', ' '))


def add_currency_name(name, iso4217):
    global db

    db_names = db['names']

    if not isinstance(iso4217, basestring):
        print "problem", name, iso4217
        return

    name = normalize_name(name)

    if name == '':
        print "name empty", iso4217
        return

    iso4217_set = db_names.get(name, None)
    if iso4217_set is not None and iso4217 not in iso4217_set:
        db_names[name].append(iso4217)
    else:
        db_names[name] = [iso4217]


def add_currency_label(label, iso4217, language):
    global db

    db['iso4217'][iso4217] = db['iso4217'].get(iso4217, {})
    db['iso4217'][iso4217][language] = label


def get_property_value(data, name):
    prop = data.get('claims', {}).get(name, {})
    if len(prop) == 0:
        return None

    value = prop[0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
    if value == '':
        return None

    return value


def parse_currency(data):
    iso4217 = get_property_value(data, 'P498')

    if iso4217 is not None:
        unit = get_property_value(data, 'P558')
        if unit is not None:
            add_currency_name(unit, iso4217)

        labels = data.get('labels', {})
        for language in languages:
            name = labels.get(language, {}).get('value', None)
            if name is not None:
                add_currency_name(name, iso4217)
                add_currency_label(name, iso4217, language)

        aliases = data.get('aliases', {})
        for language in aliases:
            for i in range(0, len(aliases[language])):
                alias = aliases[language][i].get('value', None)
                add_currency_name(alias, iso4217)


def fetch_data(wikidata_ids):
    url = url_template.format(query=urlencode({'ids': '|'.join(wikidata_ids)}))
    htmlresponse = get(url)
    jsonresponse = json.loads(htmlresponse.content)
    entities = jsonresponse.get('entities', {})

    for pname in entities:
        pvalue = entities.get(pname)
        parse_currency(pvalue)


def add_q(i):
    return "Q" + str(i)


def fetch_data_batch(wikidata_ids):
    while len(wikidata_ids) > 0:
        if len(wikidata_ids) > 50:
            fetch_data(wikidata_ids[0:49])
            wikidata_ids = wikidata_ids[50:]
        else:
            fetch_data(wikidata_ids)
            wikidata_ids = []


def wdq_query(query):
    url = url_wmflabs_template + query
    htmlresponse = get(url)
    jsonresponse = json.loads(htmlresponse.content)
    qlist = map(add_q, jsonresponse.get('items', {}))
    error = jsonresponse.get('status', {}).get('error', None)
    if error is not None and error != 'OK':
        print "error for query '" + query + "' :" + error

    fetch_data_batch(qlist)


def wd_query(query, offset=0):
    qlist = []

    url = url_wikidata_search_template.format(query=urlencode({'srsearch': query, 'srlimit': 50, 'sroffset': offset}))
    htmlresponse = get(url)
    jsonresponse = json.loads(htmlresponse.content)
    for r in jsonresponse.get('query', {}).get('search', {}):
        qlist.append(r.get('title', ''))
    fetch_data_batch(qlist)


# fetch #
for q in wmflabs_queries:
    wdq_query(q)

# static
add_currency_name(u"euro", 'EUR')
add_currency_name(u"euros", 'EUR')
add_currency_name(u"dollar", 'USD')
add_currency_name(u"dollars", 'USD')
add_currency_name(u"peso", 'MXN')
add_currency_name(u"pesos", 'MXN')

# write
f = open("currencies.json", "wb")
json.dump(db, f, indent=4, encoding="utf-8")
f.close()
