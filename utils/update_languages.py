# -*- coding: utf-8 -*-

# This script generates languages.py from
# intersecting each engine's supported languages.
#
# The language's native names are obtained from
# Wikipedia and Google's supported languages.
#
# The country names are obtained from http://api.geonames.org
# which requires registering as a user.
#
# Output file (languages.py) is written in current directory
# to avoid overwriting in case something goes wrong.

from requests import get
from urllib import urlencode
from lxml.html import fromstring
from json import loads
from sys import path
path.append('../searx')
from searx.engines import engines

# list of names
wiki_languages_url = 'https://meta.wikimedia.org/wiki/List_of_Wikipedias'
google_languages_url = 'https://www.google.com/preferences?#languages'
country_names_url = 'http://api.geonames.org/countryInfoJSON?{parameters}'

geonames_user = ''  # add user name here

google_json_name = 'google.preferences.langMap'

languages = {}


# To filter out invalid codes and dialects.
def valid_code(lang_code):
    # filter invalid codes
    # sl-SL is technically not invalid, but still a mistake
    if lang_code[:2] == 'xx'\
       or lang_code == 'sl-SL'\
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
        print json
        return ''

    return content[0].get('countryName', '')


# Get language names from Wikipedia.
def get_wikipedia_languages():
    response = get(wiki_languages_url)
    dom = fromstring(response.text)
    tables = dom.xpath('//table[contains(@class,"sortable")]')
    for table in tables:
        # exclude header row
        trs = table.xpath('.//tr')[1:]
        for tr in trs:
            td = tr.xpath('./td')
            code = td[3].xpath('./a')[0].text
            name = td[2].xpath('./a')[0].text
            english_name = td[1].xpath('./a')[0].text
            articles = int(td[4].xpath('./a/b')[0].text.replace(',',''))
            
            # exclude language variants and languages with few articles
            if code not in languages and articles >= 10000 and valid_code(code):
                languages[code] = (name, '', english_name)


# Get language names from Google.
def get_google_languages():
    response = get(google_languages_url)
    dom = fromstring(response.text)
    options = dom.xpath('//select[@name="hl"]/option')
    for option in options:
        code = option.xpath('./@value')[0].split('-')[0]
        name = option.text[:-1].title()

        if code not in languages and valid_code(code):
            languages[code] = (name, '', '')


# Join all language lists.
# iterate all languages supported by each engine
def join_language_lists():
    for engine_name in engines:
        for locale in engines[engine_name].supported_languages:
            locale = locale.replace('_', '-')
            if locale not in languages and valid_code(locale):
                # try to get language name
                language = languages.get(locale.split('-')[0], None)
                if language == None:
                    print engine_name + ": " + locale
                    continue

                country = get_country_name(locale)
                languages[locale] = (language[0], country, language[2])


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
    new_file = open('languages.py', 'w')
    file_content = '# -*- coding: utf-8 -*-\n'
    file_content += '# list of language codes\n'
    file_content += '# this file is generated automatically by utils/update_search_languages.py\n'
    file_content += '\nlanguage_codes = ('
    for code in sorted(languages):
        (name, country, english) = languages[code]
        file_content += '\n    (u"' + code + '"'\
                        + ', u"' + name + '"'\
                        + ', u"' + country + '"'\
                        + ', u"' + english + '"),'
    # remove last comma
    file_content = file_content[:-1]
    file_content += '\n)\n'
    new_file.write(file_content.encode('utf8'))
    new_file.close()


if __name__ == "__main__":
    get_wikipedia_languages()
    get_google_languages()
    join_language_lists()
    filter_single_country_languages()
    write_languages_file()
