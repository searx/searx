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
from searx import settings
from searx.engines import initialize_engines, engines

# Geonames API for country names.
geonames_user = ''  # ADD USER NAME HERE
country_names_url = 'http://api.geonames.org/countryInfoJSON?{parameters}'

# Output files.
engines_languages_file = 'engines_languages.json'
languages_file = 'languages.py'

engines_languages = {}


# To filter out invalid codes and dialects.
def valid_code(lang_code):
    # filter invalid codes
    # sl-SL is technically not invalid, but still a mistake
    invalid_codes = ['sl-SL', 'wt-WT', 'jw']
    invalid_countries = ['UK', 'XA', 'XL']
    if lang_code[:2] == 'xx'\
       or lang_code in invalid_codes\
       or lang_code[-2:] in invalid_countries\
       or is_dialect(lang_code):
        return False

    return True


# Language codes with any additional tags other than language and country.
def is_dialect(lang_code):
    lang_code = lang_code.split('-')
    if len(lang_code) > 2 or len(lang_code[0]) > 3:
        return True
    if len(lang_code) == 2 and len(lang_code[1]) > 2:
        return True

    return False


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
    initialize_engines(settings['engines'])
    for engine_name in engines:
        if hasattr(engines[engine_name], 'fetch_supported_languages'):
            try:
                engines_languages[engine_name] = engines[engine_name].fetch_supported_languages()
            except Exception as e:
                print e

    # write json file
    with io.open(engines_languages_file, "w", encoding="utf-8") as f:
        f.write(unicode(dumps(engines_languages, ensure_ascii=False, encoding="utf-8")))


# Join all language lists.
# Iterate all languages supported by each engine.
def join_language_lists():
    global languages
    # include wikipedia first for more accurate language names
    languages = {code: lang for code, lang
                 in engines_languages['wikipedia'].iteritems()
                 if valid_code(code)}

    for engine_name in engines_languages:
        for locale in engines_languages[engine_name]:
            if valid_code(locale):
                # if language is not on list or if it has no name yet
                if locale not in languages or not languages[locale].get('name'):
                    if isinstance(engines_languages[engine_name], dict):
                        languages[locale] = engines_languages[engine_name][locale]
                    else:
                        languages[locale] = {}

            # add to counter of engines that support given language
            lang = locale.split('-')[0]
            if lang in languages:
                if 'counter' not in languages[lang]:
                    languages[lang]['counter'] = [engine_name]
                elif engine_name not in languages[lang]['counter']:
                    languages[lang]['counter'].append(engine_name)

    # filter list to include only languages supported by most engines
    min_supported_engines = int(0.70 * len(engines_languages))
    languages = {code: lang for code, lang
                 in languages.iteritems()
                 if len(lang.get('counter', [])) >= min_supported_engines or
                 len(languages.get(code.split('-')[0], {}).get('counter', [])) >= min_supported_engines}

    # get locales that have no name or country yet
    for locale in languages.keys():
        # try to get language names
        if not languages[locale].get('name'):
            name = languages.get(locale.split('-')[0], {}).get('name', None)
            if name:
                languages[locale]['name'] = name
            else:
                # filter out locales with no name
                del languages[locale]
                continue

        # try to get language name in english
        if not languages[locale].get('english_name'):
            languages[locale]['english_name'] = languages.get(locale.split('-')[0], {}).get('english_name', '')

        # try to get country name
        if locale.find('-') > 0 and not languages[locale].get('country'):
            languages[locale]['country'] = get_country_name(locale) or ''


# Remove countryless language if language is featured in only one country.
def filter_single_country_languages():
    prev_lang = None
    prev_code = None
    for code in sorted(languages):
        lang = code.split('-')[0]
        if lang == prev_lang:
            countries += 1
        else:
            if prev_lang is not None and countries == 1:
                del languages[prev_lang]
                languages[prev_code]['country'] = ''
            countries = 0
            prev_lang = lang
        prev_code = code


# Write languages.py.
def write_languages_file():
    new_file = open(languages_file, 'w')
    file_content = '# -*- coding: utf-8 -*-\n'\
                   + '# list of language codes\n'\
                   + '# this file is generated automatically by utils/update_search_languages.py\n'\
                   + '\nlanguage_codes = ('
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
