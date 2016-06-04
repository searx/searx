import json

from searx import logger
from searx.poolrequests import get
from searx.utils import format_date_by_locale

from datetime import datetime
from dateutil.parser import parse as dateutil_parse
from urllib import urlencode
from lxml.html import fromstring


logger = logger.getChild('wikidata')
result_count = 1
wikidata_host = 'https://www.wikidata.org'
url_search = wikidata_host \
    + '/wiki/Special:ItemDisambiguation?{query}'

wikidata_api = wikidata_host + '/w/api.php'
url_detail = wikidata_api\
    + '?action=wbgetentities&format=json'\
    + '&props=labels%7Cinfo%7Csitelinks'\
    + '%7Csitelinks%2Furls%7Cdescriptions%7Cclaims'\
    + '&{query}'
url_map = 'https://www.openstreetmap.org/'\
    + '?lat={latitude}&lon={longitude}&zoom={zoom}&layers=M'
url_entity_label = wikidata_api\
    + '?action=wbgetentities&format=json&props=labels&{query}'

wikidata_ids_xpath = '//div/ul[@class="wikibase-disambiguation"]/li/a/@title'


def request(query, params):
    language = params['language'].split('_')[0]
    if language == 'all':
        language = 'en'

    params['url'] = url_search.format(
        query=urlencode({'label': query,
                        'language': language}))
    return params


def response(resp):
    results = []
    html = fromstring(resp.content)
    wikidata_ids = html.xpath(wikidata_ids_xpath)

    language = resp.search_params['language'].split('_')[0]
    if language == 'all':
        language = 'en'

    url = url_detail.format(query=urlencode({'ids': '|'.join(wikidata_ids),
                                            'languages': language + '|en'}))

    htmlresponse = get(url)
    jsonresponse = json.loads(htmlresponse.content)
    for wikidata_id in wikidata_ids[:result_count]:
        results = results + getDetail(jsonresponse, wikidata_id, language, resp.search_params['language'])

    return results


def getDetail(jsonresponse, wikidata_id, language, locale):
    results = []
    urls = []
    attributes = []

    result = jsonresponse.get('entities', {}).get(wikidata_id, {})

    title = result.get('labels', {}).get(language, {}).get('value', None)
    if title is None:
        title = result.get('labels', {}).get('en', {}).get('value', None)
    if title is None:
        return results

    description = result\
        .get('descriptions', {})\
        .get(language, {})\
        .get('value', None)

    if description is None:
        description = result\
            .get('descriptions', {})\
            .get('en', {})\
            .get('value', '')

    claims = result.get('claims', {})
    official_website = get_string(claims, 'P856', None)
    if official_website is not None:
        urls.append({'title': get_label('P856', language), 'url': official_website})
        results.append({'title': title, 'url': official_website})

    wikipedia_link_count = 0
    wikipedia_link = get_wikilink(result, language + 'wiki')
    wikipedia_link_count += add_url(urls,
                                    'Wikipedia (' + language + ')',
                                    wikipedia_link)
    if language != 'en':
        wikipedia_en_link = get_wikilink(result, 'enwiki')
        wikipedia_link_count += add_url(urls,
                                        'Wikipedia (en)',
                                        wikipedia_en_link)
    if wikipedia_link_count == 0:
        misc_language = get_wiki_firstlanguage(result, 'wiki')
        if misc_language is not None:
            add_url(urls,
                    'Wikipedia (' + misc_language + ')',
                    get_wikilink(result, misc_language + 'wiki'))

    if language != 'en':
        add_url(urls,
                'Wiki voyage (' + language + ')',
                get_wikilink(result, language + 'wikivoyage'))

    add_url(urls,
            'Wiki voyage (en)',
            get_wikilink(result, 'enwikivoyage'))

    if language != 'en':
        add_url(urls,
                'Wikiquote (' + language + ')',
                get_wikilink(result, language + 'wikiquote'))

    add_url(urls,
            'Wikiquote (en)',
            get_wikilink(result, 'enwikiquote'))

    add_url(urls,
            'Commons wiki',
            get_wikilink(result, 'commonswiki'))

    # Location
    add_url(urls,
            get_label('P625', language),
            get_geolink(claims, 'P625', None))

    add_url(urls,
            'Wikidata',
            'https://www.wikidata.org/wiki/'
            + wikidata_id + '?uselang=' + language)

    musicbrainz_work_id = get_string(claims, 'P435')
    if musicbrainz_work_id is not None:
        add_url(urls,
                'MusicBrainz',
                'http://musicbrainz.org/work/'
                + musicbrainz_work_id)

    musicbrainz_artist_id = get_string(claims, 'P434')
    if musicbrainz_artist_id is not None:
        add_url(urls,
                'MusicBrainz',
                'http://musicbrainz.org/artist/'
                + musicbrainz_artist_id)

    musicbrainz_release_group_id = get_string(claims, 'P436')
    if musicbrainz_release_group_id is not None:
        add_url(urls,
                'MusicBrainz',
                'http://musicbrainz.org/release-group/'
                + musicbrainz_release_group_id)

    musicbrainz_label_id = get_string(claims, 'P966')
    if musicbrainz_label_id is not None:
        add_url(urls,
                'MusicBrainz',
                'http://musicbrainz.org/label/'
                + musicbrainz_label_id)

    # musicbrainz_area_id = get_string(claims, 'P982')
    # P1407 MusicBrainz series ID
    # P1004 MusicBrainz place ID
    # P1330 MusicBrainz instrument ID
    # P1407 MusicBrainz series ID

    postal_code = get_string(claims, 'P281', None)
    if postal_code is not None:
        attributes.append({'label': get_label('P281', language), 'value': postal_code})

    date_of_birth = get_time(claims, 'P569', locale, None)
    if date_of_birth is not None:
        attributes.append({'label': get_label('P569', language), 'value': date_of_birth})

    date_of_death = get_time(claims, 'P570', locale, None)
    if date_of_death is not None:
        attributes.append({'label': get_label('P570', language), 'value': date_of_death})

    if len(attributes) == 0 and len(urls) == 2 and len(description) == 0:
        results.append({
                       'url': urls[0]['url'],
                       'title': title,
                       'content': description
                       })
    else:
        results.append({
                       'infobox': title,
                       'id': wikipedia_link,
                       'content': description,
                       'attributes': attributes,
                       'urls': urls
                       })

    return results


def add_url(urls, title, url):
    if url is not None:
        urls.append({'title': title, 'url': url})
        return 1
    else:
        return 0


def get_mainsnak(claims, propertyName):
    propValue = claims.get(propertyName, {})
    if len(propValue) == 0:
        return None

    propValue = propValue[0].get('mainsnak', None)
    return propValue


def get_string(claims, propertyName, defaultValue=None):
    propValue = claims.get(propertyName, {})
    if len(propValue) == 0:
        return defaultValue

    result = []
    for e in propValue:
        mainsnak = e.get('mainsnak', {})

        datavalue = mainsnak.get('datavalue', {})
        if datavalue is not None:
            result.append(datavalue.get('value', ''))

    if len(result) == 0:
        return defaultValue
    else:
        # TODO handle multiple urls
        return result[0]


def get_time(claims, propertyName, locale, defaultValue=None):
    propValue = claims.get(propertyName, {})
    if len(propValue) == 0:
        return defaultValue

    result = []
    for e in propValue:
        mainsnak = e.get('mainsnak', {})

        datavalue = mainsnak.get('datavalue', {})
        if datavalue is not None:
            value = datavalue.get('value', '')
            result.append(value.get('time', ''))

    if len(result) == 0:
        date_string = defaultValue
    else:
        date_string = ', '.join(result)

    try:
        parsed_date = datetime.strptime(date_string, "+%Y-%m-%dT%H:%M:%SZ")
    except:
        if date_string.startswith('-'):
            return date_string.split('T')[0]
        try:
            parsed_date = dateutil_parse(date_string, fuzzy=False, default=False)
        except:
            logger.debug('could not parse date %s', date_string)
            return date_string.split('T')[0]

    return format_date_by_locale(parsed_date, locale)


def get_geolink(claims, propertyName, defaultValue=''):
    mainsnak = get_mainsnak(claims, propertyName)

    if mainsnak is None:
        return defaultValue

    datatype = mainsnak.get('datatype', '')
    datavalue = mainsnak.get('datavalue', {})

    if datatype != 'globe-coordinate':
        return defaultValue

    value = datavalue.get('value', {})

    precision = value.get('precision', 0.0002)

    # there is no zoom information, deduce from precision (error prone)
    # samples :
    # 13 --> 5
    # 1 --> 6
    # 0.016666666666667 --> 9
    # 0.00027777777777778 --> 19
    # wolframalpha :
    # quadratic fit { {13, 5}, {1, 6}, {0.0166666, 9}, {0.0002777777,19}}
    # 14.1186-8.8322 x+0.625447 x^2
    if precision < 0.0003:
        zoom = 19
    else:
        zoom = int(15 - precision * 8.8322 + precision * precision * 0.625447)

    url = url_map\
        .replace('{latitude}', str(value.get('latitude', 0)))\
        .replace('{longitude}', str(value.get('longitude', 0)))\
        .replace('{zoom}', str(zoom))

    return url


def get_wikilink(result, wikiid):
    url = result.get('sitelinks', {}).get(wikiid, {}).get('url', None)
    if url is None:
        return url
    elif url.startswith('http://'):
        url = url.replace('http://', 'https://')
    elif url.startswith('//'):
        url = 'https:' + url
    return url


def get_wiki_firstlanguage(result, wikipatternid):
    for k in result.get('sitelinks', {}).keys():
        if k.endswith(wikipatternid) and len(k) == (2 + len(wikipatternid)):
            return k[0:2]
    return None


def get_label(entity_id, language):
    url = url_entity_label.format(query=urlencode({'ids': entity_id,
                                                   'languages': language + '|en'}))

    response = get(url)
    jsonresponse = json.loads(response.text)
    label = jsonresponse.get('entities', {}).get(entity_id, {}).get('labels', {}).get(language, {}).get('value', None)
    if label is None:
        label = jsonresponse['entities'][entity_id]['labels']['en']['value']

    return label
