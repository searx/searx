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
from lxml.html import fromstring
from searx.url_utils import quote, urlencode

# search-url
base_url = u'https://{language}.wikipedia.org/'
search_url = base_url + u'w/api.php?'\
    'action=query'\
    '&format=json'\
    '&{query}'\
    '&prop=extracts|pageimages'\
    '&exintro'\
    '&explaintext'\
    '&pithumbsize=300'\
    '&redirects'
supported_languages_url = 'https://meta.wikimedia.org/wiki/List_of_Wikipedias'


# set language in base_url
def url_lang(lang):
    lang = lang.split('-')[0]
    if lang == 'all' or lang not in supported_languages:
        language = 'en'
    else:
        language = lang

    return language


# do search-request
def request(query, params):
    if query.islower():
        query = u'{0}|{1}'.format(query.decode('utf-8'), query.decode('utf-8').title()).encode('utf-8')

    params['url'] = search_url.format(query=urlencode({'titles': query}),
                                      language=url_lang(params['language']))

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

    search_result = loads(resp.text)

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

    # link to wikipedia article
    wikipedia_link = base_url.format(language=url_lang(resp.search_params['language'])) \
        + 'wiki/' + quote(title.replace(' ', '_').encode('utf8'))

    results.append({'url': wikipedia_link, 'title': title})

    results.append({'infobox': title,
                    'id': wikipedia_link,
                    'content': summary,
                    'img_src': image,
                    'urls': [{'title': 'Wikipedia', 'url': wikipedia_link}]})

    return results


# get supported languages from their site
def _fetch_supported_languages(resp):
    supported_languages = {}
    dom = fromstring(resp.text)
    tables = dom.xpath('//table[contains(@class,"sortable")]')
    for table in tables:
        # exclude header row
        trs = table.xpath('.//tr')[1:]
        for tr in trs:
            td = tr.xpath('./td')
            code = td[3].xpath('./a')[0].text
            name = td[2].xpath('./a')[0].text
            english_name = td[1].xpath('./a')[0].text
            articles = int(td[4].xpath('./a/b')[0].text.replace(',', ''))
            # exclude languages with too few articles
            if articles >= 100:
                supported_languages[code] = {"name": name, "english_name": english_name, "articles": articles}

    return supported_languages
