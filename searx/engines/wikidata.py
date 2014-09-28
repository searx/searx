import json
from datetime import datetime
from requests import get
from urllib import urlencode

resultCount=2
urlSearch = 'https://www.wikidata.org/w/api.php?action=query&list=search&format=json&srnamespace=0&srprop=sectionsnippet&{query}'
urlDetail = 'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=labels%7Cinfo%7Csitelinks%7Csitelinks%2Furls%7Cdescriptions%7Cclaims&{query}'
# find the right URL for urlMap
urlMap = 'http://www.openstreetmap.org/?lat={latitude}&lon={longitude}&zoom={zoom}&layers=M'

def request(query, params):
    params['url'] = urlSearch.format(query=urlencode({'srsearch': query, 'srlimit': resultCount}))
    print params['url']
    return params


def response(resp):
    results = []
    search_res = json.loads(resp.text)
    # TODO parallel http queries
    before = datetime.now()
    for r in search_res.get('query', {}).get('search', {}):
        wikidata_id = r.get('title', '')
        results = results + getDetail(wikidata_id)
    after = datetime.now()
    print str(after - before) + " second(s)"

    return results

def getDetail(wikidata_id):
    language = 'fr'

    url = urlDetail.format(query=urlencode({'ids': wikidata_id, 'languages': language + '|en'}))
    print url
    response = get(url)
    result = json.loads(response.content)
    result = result.get('entities', {}).get(wikidata_id, {})
    
    title = result.get('labels', {}).get(language, {}).get('value', None)
    if title == None:
        title = result.get('labels', {}).get('en', {}).get('value', wikidata_id)
    results = []
    urls = []
    attributes = []

    description = result.get('descriptions', {}).get(language, {}).get('value', '')
    if description == '':
        description = result.get('descriptions', {}).get('en', {}).get('value', '')

    claims = result.get('claims', {})
    official_website = get_string(claims, 'P856', None)
    print official_website
    if official_website != None:
        urls.append({ 'title' : 'Official site', 'url': official_website })
        results.append({ 'title': title, 'url' : official_website })

    if language != 'en':
        add_url(urls, 'Wikipedia (' + language + ')', get_wikilink(result, language + 'wiki'))
    wikipedia_en_link = get_wikilink(result, 'enwiki')
    add_url(urls, 'Wikipedia (en)', wikipedia_en_link)

    if language != 'en':
        add_url(urls, 'Wiki voyage (' + language + ')', get_wikilink(result, language + 'wikivoyage'))
    add_url(urls, 'Wiki voyage (en)', get_wikilink(result, 'enwikivoyage'))

    if language != 'en':
        add_url(urls, 'Wikiquote (' + language + ')', get_wikilink(result, language + 'wikiquote'))
    add_url(urls, 'Wikiquote (en)', get_wikilink(result, 'enwikiquote'))


    add_url(urls, 'Commons wiki', get_wikilink(result, 'commonswiki'))

    add_url(urls, 'Location', get_geolink(claims, 'P625', None))

    add_url(urls, 'Wikidata', 'https://www.wikidata.org/wiki/' + wikidata_id + '?uselang='+ language)

    postal_code = get_string(claims, 'P281', None)
    if postal_code != None:
        attributes.append({'label' : 'Postal code(s)', 'value' : postal_code})

    date_of_birth = get_time(claims, 'P569', None)
    if date_of_birth != None:
        attributes.append({'label' : 'Date of birth', 'value' : date_of_birth})

    date_of_death = get_time(claims, 'P570', None)
    if date_of_death != None:
        attributes.append({'label' : 'Date of death', 'value' : date_of_death})


    results.append({
            'infobox' : title, 
            'id' : wikipedia_en_link,
            'content' : description,
            'attributes' : attributes,
            'urls' : urls
            })

    return results

def add_url(urls, title, url):
    if url != None:
        urls.append({'title' : title, 'url' : url})

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

        datatype = mainsnak.get('datatype', '')
        datavalue = mainsnak.get('datavalue', {})
        if datavalue != None:
            result.append(datavalue.get('value', ''))

    if len(result) == 0:
        return defaultValue
    else:
        return ', '.join(result)

def get_time(claims, propertyName, defaultValue=None):
    propValue = claims.get(propertyName, {})
    if len(propValue) == 0:
        return defaultValue

    result = []
    for e in propValue:
        mainsnak = e.get('mainsnak', {})

        datatype = mainsnak.get('datatype', '')
        datavalue = mainsnak.get('datavalue', {})
        if datavalue != None:
            value = datavalue.get('value', '')
            result.append(value.get('time', ''))

    if len(result) == 0:
        return defaultValue
    else:
        return ', '.join(result)

def get_geolink(claims, propertyName, defaultValue=''):
    mainsnak = get_mainsnak(claims, propertyName)

    if mainsnak == None:
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
    # wolframalpha : quadratic fit { {13, 5}, {1, 6}, {0.0166666, 9}, {0.0002777777,19}}
    # 14.1186-8.8322 x+0.625447 x^2
    if precision < 0.0003:
        zoom = 19
    else:
        zoom = int(15 - precision*8.8322 + precision*precision*0.625447)

    url = urlMap.replace('{latitude}', str(value.get('latitude',0))).replace('{longitude}', str(value.get('longitude',0))).replace('{zoom}', str(zoom))

    return url

def get_wikilink(result, wikiid):
    url = result.get('sitelinks', {}).get(wikiid, {}).get('url', None)
    if url == None:
        return url
    elif url.startswith('http://'):
        url = url.replace('http://', 'https://')
    elif url.startswith('//'):
        url = 'https:' + url
    return url
