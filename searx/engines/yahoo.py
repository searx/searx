"""
 Yahoo (Web)

 @website     https://search.yahoo.com/web
 @provide-api yes (https://developer.yahoo.com/boss/search/),
              $0.80/1000 queries

 @using-api   no (because pricing)
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content, suggestion
"""

from lxml import html
from searx.engines.xpath import extract_text, extract_url
from searx.url_utils import unquote, urlencode
from searx.utils import match_language

# engine dependent config
categories = ['general']
paging = True
language_support = True
time_range_support = True

# search-url
# Specifying language with "&vl=lang_{lang}", eg "vl=lang_it" has some effect, but not much.
# Using dedicated subdomains is better, but doesn't work well for all languages (and sometimes
# they don't exist at all). Using eg. "fr2=sb-top-it.search" combined with subdomain has good
# effect. Using all three seem to force the results into that language most of the time.
default_base_url = 'https://search.yahoo.com/'
search_url = 'search?{query}&b={offset}&fl=1&vl=lang_{lang}&fr2={fr2}'
search_url_with_time = 'search?{query}&b={offset}&fl=1&vl=lang_{lang}&fr2={fr2}&age={age}&btf={btf}&fr2=time'

supported_languages_url = 'https://search.yahoo.com/web/advanced'
# The (advanced) language page only lists the iso-639-1 codes, even though form iso-639-1 '-' iso-3166 is supported.
# We use this extended list for languages that have regional variations that are supported by yahoo and where
# the <country_code>.search.yahoo.com DNS entry exists. These have been found manually:
extended_supported_languages = set([
    'da-DK',
    'de-AT',
    'de-CH',
    'de-DE',
    'en-AU',
    'en-CA',
    'en-IE',
    'en-NZ',
    'en-UK',
    'en-ZA',
    'es-CO',
    'es-ES',
    'es-MX',
    'fi-FI',
    'fr-BE',
    'fr-CA',
    'fr-CH',
    'fr-FR',
    'hu-HU',
    'it-IT',
    'nb-NO',
    'nn-NO',
    'no-NO',
    'nl-BE',
    'nl-NL',
    'pl-PL',
    'pt-BR',
    'pt-PT',
    'ro-RO',
    'sv-SE',
])
extended_supported_languages_lowercase = set([s.lower() for s in extended_supported_languages])

# specific xpath variables
results_xpath = "//div[contains(concat(' ', normalize-space(@class), ' '), ' Sr ')]"
url_xpath = './/h3/a/@href'
title_xpath = './/h3/a'
content_xpath = './/div[@class="compText aAbs"]'
suggestion_xpath = "//div[contains(concat(' ', normalize-space(@class), ' '), ' AlsoTry ')]//a"

time_range_dict = {'day': ['1d', 'd'],
                   'week': ['1w', 'w'],
                   'month': ['1m', 'm']}

language_aliases = {'zh-CN': 'zh-CHS', 'zh-TW': 'zh-CHT', 'zh-HK': 'zh-CHT'}


# Choose the best (base-url,sb-top-thing) for a given language
def base_url_and_parameter_for_language(lang):
    lang = lang.lower()
    if lang in extended_supported_languages_lowercase:
        #lang-country has extended support
        country = lang.split('-')[1]
        base_url = "https://" + country + ".search.yahoo.com/"
        fr2 = "sb-top-" + country + ".search"
        return (base_url,fr2)
    # is it for a 1:1 lang-country (eg fi-fi)?
    number_of_lang_matches = 0
    lang_match = None
    for lang_country in extended_supported_languages_lowercase:
        if lang.split('-')[0] == lang_country.split('-')[0]:
            number_of_lang_matches += 1
            lang_match = lang_country
    if number_of_lang_matches == 1:
        # found a single match on language, so it must be a the case of lang='xx' and extended_supported_languages_lowercase having element 'xx-yy'
        # assume there is a 1:1 between language and country, eg sv-se.
        country = lang_match.split('-')[1]
        base_url = "https://" + country + ".search.yahoo.com/"
        fr2 = "sb-top-" + country + ".search"
        return (base_url,fr2)
    elif number_of_lang_matches>1:
        # The language is used in multiple countries and the user specified the language only (no country/region).
        # It is best not to use strong hints because otherwise we may get irrelevant results for the user.
        # Eg. if we get the query "billets d'avion pour Berlin" and lang=fr, then we don't wnat to focus it on
        # french-french results because it could be a canadian, belgian or swiss, and all the fabulous offers from
        # CDG are that relevant.
        pass
    # no country specified in language code or unknown language so we can't pick a subdomain
    return (default_base_url,"sb-top-search")


# remove yahoo-specific tracking-url
def parse_url(url_string):
    endings = ['/RS', '/RK']
    endpositions = []
    start = url_string.find('http', url_string.find('/RU=') + 1)

    for ending in endings:
        endpos = url_string.rfind(ending)
        if endpos > -1:
            endpositions.append(endpos)

    if start == 0 or len(endpositions) == 0:
        return url_string
    else:
        end = min(endpositions)
        return unquote(url_string[start:end])


def _get_url(query, offset, language, time_range):
    (base_url,fr2) = base_url_and_parameter_for_language(language)
    if time_range in time_range_dict:
        return base_url + search_url_with_time.format(offset=offset,
                                                      query=urlencode({'p': query}),
                                                      lang=language.replace('-', '_').lower(),
                                                      fr2=fr2,
                                                      age=time_range_dict[time_range][0],
                                                      btf=time_range_dict[time_range][1])
    return base_url + search_url.format(offset=offset,
                                        query=urlencode({'p': query}),
                                        lang=language.replace('-', '_').lower(),
                                        fr2=fr2)


# do search-request
def request(query, params):
    if params['time_range'] and params['time_range'] not in time_range_dict:
        return params

    offset = (params['pageno'] - 1) * 10 + 1
    language = match_language(params['language'], supported_languages, language_aliases)

    params['url'] = _get_url(query, offset, language, params['time_range'])

    # TODO required?
    params['cookies']['sB'] = 'fl=1&vl=lang_{lang}&sh=1&rw=new&v=1'\
        .format(lang=language.replace('-', '_').lower())

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    try:
        results_num = int(dom.xpath('//div[@class="compPagination"]/span[last()]/text()')[0]
                          .split()[0].replace(',', ''))
        results.append({'number_of_results': results_num})
    except:
        pass

    # parse results
    for result in dom.xpath(results_xpath):
        try:
            url = parse_url(extract_url(result.xpath(url_xpath), search_url))
            title = extract_text(result.xpath(title_xpath)[0])
        except:
            continue

        content = extract_text(result.xpath(content_xpath)[0])

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # if no suggestion found, return results
    suggestions = dom.xpath(suggestion_xpath)
    if not suggestions:
        return results

    # parse suggestion
    for suggestion in suggestions:
        # append suggestion
        results.append({'suggestion': extract_text(suggestion)})

    # return results
    return results


# get supported languages from their site
def _fetch_supported_languages(resp):
    supported_languages = []
    dom = html.fromstring(resp.text)
    options = dom.xpath('//div[@id="yschlang"]/span/label/input')
    for option in options:
        code_parts = option.xpath('./@value')[0][5:].split('_')
        if len(code_parts) == 2:
            code = code_parts[0] + '-' + code_parts[1].upper()
            supported_languages.append(code)
        else:
            code = code_parts[0]
            if code in extended_supported_languages:
                supported_languages.append(code)
            else:
                # The page lists only the language but not the language-regions supported.
                # Eg. only "fr" is listed but fr-CA, fr-FR, fr-BE, fr-CH are supported so
                # override with prefix-matches from extended_supported_languages
                extended_langs_matches_found = 0
                for extended_lang in extended_supported_languages:
                    if extended_lang.split('-')[0] == code:
                        supported_languages.append(extended_lang)
                        extended_langs_matches_found += 1
                if extended_langs_matches_found == 0:
                    supported_languages.append(code)

    return supported_languages
