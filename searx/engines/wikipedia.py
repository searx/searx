"""
 Wikipedia (Web)

 @website     https://{language}.wikipedia.org
 @provide-api yes

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, infobox
"""

from json import loads
from urllib import urlencode, quote

# search-url
base_url = 'https://{language}.wikipedia.org/'
search_postfix = 'w/api.php?'\
    'action=query'\
    '&format=json'\
    '&{query}'\
    '&prop=extracts|pageimages'\
    '&exintro'\
    '&explaintext'\
    '&pithumbsize=300'\
    '&redirects'


# set language in base_url
def url_lang(lang):
    if lang == 'all':
        language = 'en'
    else:
        language = lang.split('_')[0]

    return base_url.format(language=language)


# do search-request
def request(query, params):
    if query.islower():
        query += '|' + query.title()

    params['url'] = url_lang(params['language']) \
        + search_postfix.format(query=urlencode({'titles': query}))

    return params


# get first meaningful paragraph
# this should filter out disambiguation pages and notes above first paragraph
# "magic numbers" were obtained by fine tuning
def extract_first_paragraph(content, title, image):
    first_paragraph = None

    failed_attempts = 0
    for paragraph in content.split('\n'):

        starts_with_title = paragraph.lower().find(title.lower(), 0, len(title) + 35)
        length = len(paragraph)

        if length >= 200 or (starts_with_title >= 0 and (image or length >= 150)):
            first_paragraph = paragraph
            break

        failed_attempts += 1
        if failed_attempts > 3:
            return None

    return first_paragraph


# get response from search-request
def response(resp):
    results = []

    search_result = loads(resp.content)

    # wikipedia article's unique id
    # first valid id is assumed to be the requested article
    for article_id in search_result['query']['pages']:
        page = search_result['query']['pages'][article_id]
        if int(article_id) > 0:
            break

    if int(article_id) < 0:
        return []

    title = page.get('title')

    image = page.get('thumbnail')
    if image:
        image = image.get('source')

    extract = page.get('extract')

    summary = extract_first_paragraph(extract, title, image)
    if not summary:
        return []

    # link to wikipedia article
    wikipedia_link = url_lang(resp.search_params['language']) \
        + 'wiki/' + quote(title.replace(' ', '_').encode('utf8'))

    results.append({'url': wikipedia_link, 'title': title})

    results.append({'infobox': title,
                    'id': wikipedia_link,
                    'content': summary,
                    'img_src': image,
                    'urls': [{'title': 'Wikipedia', 'url': wikipedia_link}]})

    return results
