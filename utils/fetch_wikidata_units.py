#!/usr/bin/env python

import json
import collections

# set path
from sys import path
from os.path import realpath, dirname, join
path.append(realpath(dirname(realpath(__file__)) + '/../'))

from searx import searx_dir
from searx.engines.wikidata import send_wikidata_query


SARQL_REQUEST = """
SELECT DISTINCT ?item ?symbol ?P2370 ?P2370Unit ?P2442 ?P2442Unit
WHERE
{
?item wdt:P31/wdt:P279 wd:Q47574.
?item wdt:P5061 ?symbol.
FILTER(LANG(?symbol) = "en").
}
ORDER BY ?item
"""


def get_data():
    def get_key(unit):
        return unit['item']['value'].replace('http://www.wikidata.org/entity/', '')

    def get_value(unit):
        return unit['symbol']['value']

    result = send_wikidata_query(SARQL_REQUEST)
    if result is not None:
        # sort the unit by entity name
        # so different fetchs keep the file unchanged.
        list(result['results']['bindings']).sort(key=get_key)
        return collections.OrderedDict([(get_key(unit), get_value(unit)) for unit in result['results']['bindings']])


def get_wikidata_units_filename():
    return join(join(searx_dir, "data"), "wikidata_units.json")


with open(get_wikidata_units_filename(), 'w') as f:
    json.dump(get_data(), f, indent=4, ensure_ascii=False)
