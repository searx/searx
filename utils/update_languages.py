# -*- coding: utf-8 -*-

# This script generates languages.py from
# intersecting each engine's supported languages.
#
# The language's native names are obtained from
# Wikipedia's supported languages.
#
# Output file (languages.py) is written in current directory
# to avoid overwriting in case something goes wrong.

from requests import get
from re import sub
from lxml.html import fromstring
from json import loads
from sys import path
path.append('../searx')
from searx.engines import engines

# list of language names
wiki_languages_url = 'https://meta.wikimedia.org/wiki/List_of_Wikipedias'
google_languages_url = 'https://www.google.com/preferences?#languages'

google_json_name = 'google.preferences.langMap'

languages = {}

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
            
            if code not in languages:
                languages[code] = (name, '', english_name)

# Get language names from Google.
def get_google_languages():
    response = get(google_languages_url)
    dom = fromstring(response.text)
    options = dom.xpath('//select[@name="hl"]/option')
    for option in options:
        code = option.xpath('./@value')[0]
        name = option.text[:-1]

        if code not in languages:
            languages[code] = (name, '', '')

# Join all language lists.
# iterate all languages supported by each engine
def join_language_lists():
    for engine_name in engines:
        for locale in engines[engine_name].supported_languages:
            locale = locale.replace('_', '-')
            if locale not in languages:
                # try to get language name
                language = languages.get(locale.split('-')[0], None)
                if language == None:
                    print engine_name + ": " + locale
                    continue

                (name, country, english) = language
                languages[locale] = (name, country, english)

# Write languages.py.
def write_languages_file():
    new_file = open('languages.py', 'w')
    file_content = '# -*- coding: utf-8 -*-\n'
    file_content += '# list of language codes\n'
    file_content += '# this file is generated automatically by utils/update_search_languages.py\n'
    file_content += '\nlanguage_codes = ('
    for code in languages:
        (name, country, english) = languages[code]
        file_content += '\n    (u"' + code + '"'\
                        + ', u"' + name + '"'\
                        + ', u"' + country[1:-1] + '"'\
                        + ', u"' + english + '"),'
    # remove last comma
    file_content = file_content[:-1]
    file_content += '\n)\n'
    new_file.write(file_content.encode('utf8'))
    new_file.close()

def main():
    get_wikipedia_languages()
    get_google_languages()
    join_language_lists()
    write_languages_file()

if __name__ == "__main__":
    main()
