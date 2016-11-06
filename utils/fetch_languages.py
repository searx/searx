# -*- coding: utf-8 -*-

# This script generates languages.py from intersecting each engine's supported languages.
#
# The country names are obtained from http://api.geonames.org which requires registering as a user.
#
# Output files (engines_languages.json and languages.py)
# are written in current directory to avoid overwriting in case something goes wrong.

from requests import get
from urllib import urlencode
from lxml.html import fromstring
from json import loads, dumps
import io
from sys import path
path.append('../searx')  # noqa
from searx.engines import engines

# Geonames API for country names.
geonames_user = ''  # ADD USER NAME HERE
country_names_url = 'http://api.geonames.org/countryInfoJSON?{parameters}'

# Output files.
engines_languages_file = 'engines_languages.json'
languages_file = 'languages.py'

engines_languages = {}
languages = {}


# To filter out invalid codes and dialects.
def valid_code(lang_code):
    # filter invalid codes
    # sl-SL is technically not invalid, but still a mistake
    if lang_code[:2] == 'xx'\
       or lang_code == 'sl-SL'\
       or lang_code == 'wt-WT'\
       or lang_code == 'jw'\
       or lang_code[-2:] == 'UK'\
       or lang_code[-2:] == 'XA'\
       or lang_code[-2:] == 'XL':
        return False

    # filter dialects
    lang_code = lang_code.split('-')
    if len(lang_code) > 2 or len(lang_code[0]) > 3:
        return False
    if len(lang_code) == 2 and len(lang_code[1]) > 2:
        return False

    return True


# Get country name in specified language.
def get_country_name(locale):
    if geonames_user is '':
        return ''

    locale = locale.split('-')
    if len(locale) != 2:
        return ''

    url = country_names_url.format(parameters=urlencode({'lang': locale[0],
                                                         'country': locale[1],
                                                         'username': geonames_user}))
    response = get(url)
    json = loads(response.text)
    content = json.get('geonames', None)
    if content is None or len(content) != 1:
        print "No country name found for " + locale[0] + "-" + locale[1]
        return ''

    return content[0].get('countryName', '')


# Fetchs supported languages for each engine and writes json file with those.
def fetch_supported_languages():
    for engine_name in engines:
        if hasattr(engines[engine_name], 'fetch_supported_languages'):
            try:
                engines_languages[engine_name] = engines[engine_name].fetch_supported_languages()
            except Exception as e:
                print e

    # write json file
    f = io.open(engines_languages_file, "w", encoding="utf-8")
    f.write(unicode(dumps(engines_languages, indent=4, ensure_ascii=False, encoding="utf-8")))
    f.close()


# Join all language lists.
# Iterate all languages supported by each engine.
def join_language_lists():
    # include wikipedia first for more accurate language names
    # exclude languages with too few articles
    languages.update({code: lang for code, lang
                      in engines_languages['wikipedia'].iteritems()
                      if valid_code(code) and lang['articles'] >= 100000})

    for engine_name in engines_languages:
        for locale in engines_languages[engine_name]:
            if not valid_code(locale):
                continue

            # if language is not on list or if it has no name yet
            if locale not in languages or not languages[locale].get('name'):
                if isinstance(engines_languages[engine_name], dict) \
                  and engines_languages[engine_name][locale].get('articles', float('inf')) >= 100000:
                    languages[locale] = engines_languages[engine_name][locale]
                else:
                    languages[locale] = {}

    # get locales that have no name yet
    for locale in languages.keys():
        if not languages[locale].get('name'):
            # try to get language and country names
            name = languages.get(locale.split('-')[0], {}).get('name', None)
            if name:
                languages[locale]['name'] = name
                languages[locale]['country'] = get_country_name(locale) or ''
                languages[locale]['english_name'] = languages.get(locale.split('-')[0], {}).get('english_name', '')
            else:
                # filter out locales with no name
                del languages[locale]


# Remove countryless language if language is featured in only one country.
def filter_single_country_languages():
    prev_lang = None
    for code in sorted(languages):
        lang = code.split('-')[0]
        if lang == prev_lang:
            countries += 1
        else:
            if prev_lang is not None and countries == 1:
                del languages[prev_lang]
            countries = 0
            prev_lang = lang


# Write languages.py.
def write_languages_file():
    new_file = open(languages_file, 'w')
    file_content = '# -*- coding: utf-8 -*-\n'
    file_content += '# list of language codes\n'
    file_content += '# this file is generated automatically by utils/update_search_languages.py\n'
    file_content += '\nlanguage_codes = ('
    for code in sorted(languages):
        file_content += '\n    (u"' + code + '"'\
                        + ', u"' + languages[code]['name'].split(' (')[0] + '"'\
                        + ', u"' + languages[code].get('country', '') + '"'\
                        + ', u"' + languages[code].get('english_name', '').split(' (')[0] + '"),'
    # remove last comma
    file_content = file_content[:-1]
    file_content += '\n)\n'
    new_file.write(file_content.encode('utf8'))
    new_file.close()


if __name__ == "__main__":
    fetch_supported_languages()
    join_language_lists()
    filter_single_country_languages()
    write_languages_file()
