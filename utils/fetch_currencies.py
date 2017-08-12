# -*- coding: utf-8 -*-
import json
import re
import unicodedata
import string
import io
from urllib import urlencode
from requests import get

query = """# ?item (LANG(?label) AS ?lang) 
SELECT DISTINCT ?iso4217 ?unit ?unicode ?label ?alias WHERE {
  ?item wdt:P498 ?iso4217; rdfs:label ?label.
  OPTIONAL { ?item skos:altLabel ?alias FILTER (LANG (?alias) = LANG(?label)). }
  OPTIONAL { ?item wdt:P558 ?unit. }
  OPTIONAL { ?item wdt:P489 ?symbol.
             ?symbol wdt:P487 ?unicode. }
  FILTER(LANG(?label) IN ('de', 'en', 'es', 'fr', 'hu', 'it', 'nl', 'jp', 'hu', 'bg', 'cs', 'el', 'eo', 'fi', 'he', 'it', 'nl', 'pt', 'ro', 'ru', 'sk', 'sv', 'tr', 'uk', 'zh')).
}
ORDER BY ?item ?lang
"""

sparql_endpoint_url = 'https://query.wikidata.org/sparql'

db = {
    'iso4217': {
    },
    'names': {
    }
}


def remove_accents(data):
    return unicodedata.normalize('NFKD', data).lower()


def normalize_name(name):
    # remove right to left character (first to trim spaces after)
    name = filter(lambda c: unicodedata.category(c) != 'Cf', name)
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


def get_value(binding, key):
    return unicode(binding.get(key, {}).get('value', None))


def wd_query():
    url = sparql_endpoint_url + '?' + urlencode({'format': 'json', 'query': query})
    htmlresponse = get(url)
    jsonresponse = json.loads(htmlresponse.content, encoding="utf-8")
    for c in jsonresponse.get('results', {}).get('bindings', {}):
        iso4217 = get_value(c, 'iso4217')
        unit = get_value(c, 'unit')
        unit_unicode = get_value(c, 'unicode')
        label = get_value(c, 'label')
        alias = get_value(c, 'alias')
        language = c.get('label', {}).get('xml:lang', None)

        if label is not None:
            add_currency_label(label, iso4217, language)
            add_currency_name(label, iso4217)

        if alias is not None:
            add_currency_name(alias, iso4217)

        if unit_unicode is not None:
            add_currency_name(unit_unicode, iso4217)

        if unit is not None:
            add_currency_name(unit, iso4217)


wd_query()

# static
add_currency_name(u"euro", 'EUR')
add_currency_name(u"euros", 'EUR')
add_currency_name(u"dollar", 'USD')
add_currency_name(u"dollars", 'USD')
add_currency_name(u"peso", 'MXN')
add_currency_name(u"pesos", 'MXN')

# write
with io.open("currencies.json", "w", encoding='utf8') as f:
    j = json.dumps(db, encoding="utf-8", ensure_ascii=False)
    f.write(j)
