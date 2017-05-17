import json
from lxml import html
from re import compile
from searx.engines.xpath import extract_text
from searx.engines.duckduckgo import _fetch_supported_languages, supported_languages_url
from searx.url_utils import urlencode
from searx.utils import html_to_text

url = 'https://api.duckduckgo.com/'\
    + '?{query}&format=json&pretty=0&no_redirect=1&d=1'

http_regex = compile(r'^http:')


def result_to_text(url, text, htmlResult):
    # TODO : remove result ending with "Meaning" or "Category"
    dom = html.fromstring(htmlResult)
    a = dom.xpath('//a')
    if len(a) >= 1:
        return extract_text(a[0])
    else:
        return text


def request(query, params):
    params['url'] = url.format(query=urlencode({'q': query}))
    params['headers']['Accept-Language'] = params['language'].split('-')[0]
    return params


def response(resp):
    results = []

    search_res = json.loads(resp.text)

    content = ''
    heading = search_res.get('Heading', '')
    attributes = []
    urls = []
    infobox_id = None
    relatedTopics = []

    # add answer if there is one
    answer = search_res.get('Answer', '')
    if answer != '':
        results.append({'answer': html_to_text(answer)})

    # add infobox
    if 'Definition' in search_res:
        content = content + search_res.get('Definition', '')

    if 'Abstract' in search_res:
        content = content + search_res.get('Abstract', '')

    # image
    image = search_res.get('Image', '')
    image = None if image == '' else image

    # attributes
    if 'Infobox' in search_res:
        infobox = search_res.get('Infobox', None)
        if 'content' in infobox:
            for info in infobox.get('content'):
                attributes.append({'label': info.get('label'),
                                  'value': info.get('value')})

    # urls
    for ddg_result in search_res.get('Results', []):
        if 'FirstURL' in ddg_result:
            firstURL = ddg_result.get('FirstURL', '')
            text = ddg_result.get('Text', '')
            urls.append({'title': text, 'url': firstURL})
            results.append({'title': heading, 'url': firstURL})

    # related topics
    for ddg_result in search_res.get('RelatedTopics', []):
        if 'FirstURL' in ddg_result:
            suggestion = result_to_text(ddg_result.get('FirstURL', None),
                                        ddg_result.get('Text', None),
                                        ddg_result.get('Result', None))
            if suggestion != heading:
                results.append({'suggestion': suggestion})
        elif 'Topics' in ddg_result:
            suggestions = []
            relatedTopics.append({'name': ddg_result.get('Name', ''),
                                 'suggestions': suggestions})
            for topic_result in ddg_result.get('Topics', []):
                suggestion = result_to_text(topic_result.get('FirstURL', None),
                                            topic_result.get('Text', None),
                                            topic_result.get('Result', None))
                if suggestion != heading:
                    suggestions.append(suggestion)

    # abstract
    abstractURL = search_res.get('AbstractURL', '')
    if abstractURL != '':
        # add as result ? problem always in english
        infobox_id = abstractURL
        urls.append({'title': search_res.get('AbstractSource'),
                    'url': abstractURL})

    # definition
    definitionURL = search_res.get('DefinitionURL', '')
    if definitionURL != '':
        # add as result ? as answer ? problem always in english
        infobox_id = definitionURL
        urls.append({'title': search_res.get('DefinitionSource'),
                    'url': definitionURL})

    # to merge with wikidata's infobox
    if infobox_id:
        infobox_id = http_regex.sub('https:', infobox_id)

    # entity
    entity = search_res.get('Entity', None)
    # TODO continent / country / department / location / waterfall /
    #      mountain range :
    #      link to map search, get weather, near by locations
    # TODO musician : link to music search
    # TODO concert tour : ??
    # TODO film / actor / television  / media franchise :
    #      links to IMDB / rottentomatoes (or scrap result)
    # TODO music : link tu musicbrainz / last.fm
    # TODO book : ??
    # TODO artist / playwright : ??
    # TODO compagny : ??
    # TODO software / os : ??
    # TODO software engineer : ??
    # TODO prepared food : ??
    # TODO website : ??
    # TODO performing art : ??
    # TODO prepared food : ??
    # TODO programming language : ??
    # TODO file format : ??

    if len(heading) > 0:
        # TODO get infobox.meta.value where .label='article_title'
        if image is None and len(attributes) == 0 and len(urls) == 1 and\
           len(relatedTopics) == 0 and len(content) == 0:
            results.append({
                           'url': urls[0]['url'],
                           'title': heading,
                           'content': content
                           })
        else:
            results.append({
                           'infobox': heading,
                           'id': infobox_id,
                           'entity': entity,
                           'content': content,
                           'img_src': image,
                           'attributes': attributes,
                           'urls': urls,
                           'relatedTopics': relatedTopics
                           })

    return results
