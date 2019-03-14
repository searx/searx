# -*- coding: utf-8 -*-

# This script generates languages.py from intersecting each engine's supported languages.
#
# Output files (engines_languages.json and languages.py)
# are written in current directory to avoid overwriting in case something goes wrong.

from json import dump
import io
from sys import path
from babel import Locale, UnknownLocaleError
from babel.languages import get_global

path.append('../searx')  # noqa
from searx import settings
from searx.engines import initialize_engines, engines

# Output files.
engines_languages_file = 'engines_languages.json'
languages_file = 'languages.py'


# Fetchs supported languages for each engine and writes json file with those.
def fetch_supported_languages():
    engines_languages = {}
    for engine_name in engines:
        if hasattr(engines[engine_name], 'fetch_supported_languages'):
            try:
                engines_languages[engine_name] = engines[engine_name].fetch_supported_languages()
                if type(engines_languages[engine_name]) == list:
                    engines_languages[engine_name] = sorted(engines_languages[engine_name])
            except Exception as e:
                print(e)

    # write json file
    with io.open(engines_languages_file, "w", encoding="utf-8") as f:
        dump(engines_languages, f, ensure_ascii=False, indent=4, separators=(',', ': '))

    return engines_languages


# Get babel Locale object from lang_code if possible.
def get_locale(lang_code):
    try:
        locale = Locale.parse(lang_code, sep='-')
        return locale
    except (UnknownLocaleError, ValueError):
        return None


# Append engine_name to list of engines that support locale.
def add_engine_counter(lang_code, engine_name, languages):
    if lang_code in languages:
        if 'counter' not in languages[lang_code]:
            languages[lang_code]['counter'] = [engine_name]
        elif engine_name not in languages[lang_code]['counter']:
            languages[lang_code]['counter'].append(engine_name)


# Join all language lists.
# TODO: Add language names from engine's language list if name not known by babel.
def join_language_lists(engines_languages):
    language_list = {}
    for engine_name in engines_languages:
        for lang_code in engines_languages[engine_name]:

            # apply custom fixes if necessary
            if lang_code in getattr(engines[engine_name], 'language_aliases', {}).values():
                lang_code = next(lc for lc, alias in engines[engine_name].language_aliases.items()
                                 if lang_code == alias)

            locale = get_locale(lang_code)

            # ensure that lang_code uses standard language and country codes
            if locale and locale.territory:
                lang_code = locale.language + '-' + locale.territory

            # add locale if it's not in list
            if lang_code not in language_list:
                if locale:
                    language_list[lang_code] = {'name': locale.get_language_name().title(),
                                                'english_name': locale.english_name,
                                                'country': locale.get_territory_name() or ''}

                    # also add language without country
                    if locale.language not in language_list:
                        language_list[locale.language] = {'name': locale.get_language_name().title(),
                                                          'english_name': locale.english_name}
                else:
                    language_list[lang_code] = {}

            # count engine for both language_country combination and language alone
            add_engine_counter(lang_code, engine_name, language_list)
            add_engine_counter(lang_code.split('-')[0], engine_name, language_list)

    return language_list


# Filter language list so it only includes the most supported languages and countries.
def filter_language_list(all_languages):
    min_supported_engines = 10
    main_engines = [engine_name for engine_name in engines.keys()
                    if 'general' in engines[engine_name].categories and
                       engines[engine_name].supported_languages and
                       not engines[engine_name].disabled]

    # filter list to include only languages supported by most engines or all default general engines
    filtered_languages = {code: lang for code, lang
                          in all_languages.items()
                          if (len(lang.get('counter', [])) >= min_supported_engines or
                              all(main_engine in lang.get('counter', [])
                                  for main_engine in main_engines))}

    return filtered_languages


# Add country codes to languages without one and filter out language codes.
def assign_country_codes(filtered_languages, all_languages):
    sorted_languages = sorted(all_languages,
                              key=lambda lang: len(all_languages[lang].get('counter', [])),
                              reverse=True)
    previous_lang = None
    previous_code = None
    countries = 0
    for current_code in sorted(filtered_languages):
        current_lang = current_code.split('-')[0]

        # count country codes per language
        if current_lang == previous_lang:
            countries += 1

        else:
            if previous_lang is not None:
                # if language has no single country code
                if countries == 0:
                    # try to get country code with most supported engines
                    for l in sorted_languages:
                        l_parts = l.split('-')
                        if len(l_parts) == 2 and l_parts[0] == previous_lang:
                            filtered_languages[l] = all_languages[l]
                            filtered_languages[l]['country'] = ''
                            countries = 1
                            break

                    if countries == 0:
                        # get most likely country code from babel
                        subtags = get_global('likely_subtags').get(previous_lang)
                        if subtags:
                            subtag_parts = subtags.split('_')
                            new_code = subtag_parts[0] + '-' + subtag_parts[-1]
                            filtered_languages[new_code] = all_languages[previous_lang]
                            countries = 1

                if countries == 1:
                    # remove countryless version of language if there's only one country
                    del filtered_languages[previous_lang]
                    if previous_code in filtered_languages:
                        filtered_languages[previous_code]['country'] = ''

            countries = 0
            previous_lang = current_lang

        previous_code = current_code


# Write languages.py.
def write_languages_file(languages):
    new_file = open(languages_file, 'wb')
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
    initialize_engines(settings['engines'])
    engines_languages = fetch_supported_languages()
    all_languages = join_language_lists(engines_languages)
    filtered_languages = filter_language_list(all_languages)
    assign_country_codes(filtered_languages, all_languages)
    write_languages_file(filtered_languages)
