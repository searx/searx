"""
 general mediawiki-engine (Web)

 @website     websites built on mediawiki (https://www.mediawiki.org)
 @provide-api yes (http://www.mediawiki.org/wiki/API:Search)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title

 @todo        content
"""

from json import loads
from string import Formatter
from searx.url_utils import urlencode, quote

# engine dependent config
categories = ['general']
language_support = True
paging = True
number_of_results = 1

# search-url
base_url = 'https://{language}.wikipedia.org/'
search_postfix = 'w/api.php?action=query'\
    '&list=search'\
    '&{query}'\
    '&format=json'\
    '&sroffset={offset}'\
    '&srlimit={limit}'\
    '&srwhat=nearmatch'  # search for a near match in the title


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * number_of_results

    string_args = dict(query=urlencode({'srsearch': query}),
                       offset=offset,
                       limit=number_of_results)

    format_strings = list(Formatter().parse(base_url))

    if params['language'] == 'all':
        language = 'en'
    else:
        language = params['language'].split('-')[0]

    # format_string [('https://', 'language', '', None), ('.wikipedia.org/', None, None, None)]
    if any(x[1] == 'language' for x in format_strings):
        string_args['language'] = language

    # write search-language back to params, required in response
    params['language'] = language

    search_url = base_url + search_postfix

    params['url'] = search_url.format(**string_args)

    return params


# get response from search-request
def response(resp):
    results = []

    search_results = loads(resp.text)

    # return empty array if there are no results
    if not search_results.get('query', {}).get('search'):
        return []

    # parse results
    for result in search_results['query']['search']:
        if result.get('snippet', '').startswith('#REDIRECT'):
            continue
        url = base_url.format(language=resp.search_params['language']) +\
            'wiki/' + quote(result['title'].replace(' ', '_').encode('utf-8'))

        # append result
        results.append({'url': url,
                        'title': result['title'],
                        'content': ''})

    # return results
    return results
