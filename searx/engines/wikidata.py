# -*- coding: utf-8 -*-
"""
 Wikidata

 @website     https://wikidata.org
 @provide-api yes (https://wikidata.org/w/api.php)

 @using-api   partially (most things require scraping)
 @results     JSON, HTML
 @stable      no (html can change)
 @parse       url, infobox
"""

from searx import logger
from searx.poolrequests import get
from searx.engines.xpath import extract_text
from searx.engines.wikipedia import _fetch_supported_languages, supported_languages_url
from searx.url_utils import urlencode

from json import loads
from lxml.html import fromstring

logger = logger.getChild('wikidata')
result_count = 1

# urls
wikidata_host = 'https://www.wikidata.org'
url_search = wikidata_host \
    + '/wiki/Special:ItemDisambiguation?{query}'

wikidata_api = wikidata_host + '/w/api.php'
url_detail = wikidata_api\
    + '?action=parse&format=json&{query}'\
    + '&redirects=1&prop=text%7Cdisplaytitle%7Clanglinks%7Crevid'\
    + '&disableeditsection=1&disabletidy=1&preview=1&sectionpreview=1&disabletoc=1&utf8=1&formatversion=2'

url_map = 'https://www.openstreetmap.org/'\
    + '?lat={latitude}&lon={longitude}&zoom={zoom}&layers=M'
url_image = 'https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=500&height=400'

# xpaths
wikidata_ids_xpath = '//div/ul[@class="wikibase-disambiguation"]/li/a/@title'
title_xpath = '//*[contains(@class,"wikibase-title-label")]'
description_xpath = '//div[contains(@class,"wikibase-entitytermsview-heading-description")]'
property_xpath = '//div[@id="{propertyid}"]'
label_xpath = './/div[contains(@class,"wikibase-statementgroupview-property-label")]/a'
url_xpath = './/a[contains(@class,"external free") or contains(@class, "wb-external-id")]'
wikilink_xpath = './/ul[contains(@class,"wikibase-sitelinklistview-listview")]'\
    + '/li[contains(@data-wb-siteid,"{wikiid}")]//a/@href'
property_row_xpath = './/div[contains(@class,"wikibase-statementview")]'
preferred_rank_xpath = './/span[contains(@class,"wikibase-rankselector-preferred")]'
value_xpath = './/div[contains(@class,"wikibase-statementview-mainsnak")]'\
    + '/*/div[contains(@class,"wikibase-snakview-value")]'
language_fallback_xpath = '//sup[contains(@class,"wb-language-fallback-indicator")]'
calendar_name_xpath = './/sup[contains(@class,"wb-calendar-name")]'


def request(query, params):
    language = params['language'].split('-')[0]
    if language == 'all':
        language = 'en'

    params['url'] = url_search.format(
        query=urlencode({'label': query, 'language': language}))
    return params


def response(resp):
    results = []
    html = fromstring(resp.text)
    wikidata_ids = html.xpath(wikidata_ids_xpath)

    language = resp.search_params['language'].split('-')[0]
    if language == 'all':
        language = 'en'

    # TODO: make requests asynchronous to avoid timeout when result_count > 1
    for wikidata_id in wikidata_ids[:result_count]:
        url = url_detail.format(query=urlencode({'page': wikidata_id, 'uselang': language}))
        htmlresponse = get(url)
        jsonresponse = loads(htmlresponse.text)
        results += getDetail(jsonresponse, wikidata_id, language, resp.search_params['language'])

    return results


def getDetail(jsonresponse, wikidata_id, language, locale):
    results = []
    urls = []
    attributes = []

    title = jsonresponse.get('parse', {}).get('displaytitle', {})
    result = jsonresponse.get('parse', {}).get('text', {})

    if not title or not result:
        return results

    title = fromstring(title)
    for elem in title.xpath(language_fallback_xpath):
        elem.getparent().remove(elem)
    title = extract_text(title.xpath(title_xpath))

    result = fromstring(result)
    for elem in result.xpath(language_fallback_xpath):
        elem.getparent().remove(elem)

    description = extract_text(result.xpath(description_xpath))

    # URLS

    # official website
    add_url(urls, result, 'P856', results=results)

    # wikipedia
    wikipedia_link_count = 0
    wikipedia_link = get_wikilink(result, language + 'wiki')
    if wikipedia_link:
        wikipedia_link_count += 1
        urls.append({'title': 'Wikipedia (' + language + ')',
                     'url': wikipedia_link})

    if language != 'en':
        wikipedia_en_link = get_wikilink(result, 'enwiki')
        if wikipedia_en_link:
            wikipedia_link_count += 1
            urls.append({'title': 'Wikipedia (en)',
                         'url': wikipedia_en_link})

    # TODO: get_wiki_firstlanguage
    # if wikipedia_link_count == 0:

    # more wikis
    add_url(urls, result, default_label='Wikivoyage (' + language + ')', link_type=language + 'wikivoyage')
    add_url(urls, result, default_label='Wikiquote (' + language + ')', link_type=language + 'wikiquote')
    add_url(urls, result, default_label='Wikimedia Commons', link_type='commonswiki')

    add_url(urls, result, 'P625', 'OpenStreetMap', link_type='geo')

    # musicbrainz
    add_url(urls, result, 'P434', 'MusicBrainz', 'http://musicbrainz.org/artist/')
    add_url(urls, result, 'P435', 'MusicBrainz', 'http://musicbrainz.org/work/')
    add_url(urls, result, 'P436', 'MusicBrainz', 'http://musicbrainz.org/release-group/')
    add_url(urls, result, 'P966', 'MusicBrainz', 'http://musicbrainz.org/label/')

    # IMDb
    add_url(urls, result, 'P345', 'IMDb', 'https://www.imdb.com/', link_type='imdb')
    # source code repository
    add_url(urls, result, 'P1324')
    # blog
    add_url(urls, result, 'P1581')
    # social media links
    add_url(urls, result, 'P2397', 'YouTube', 'https://www.youtube.com/channel/')
    add_url(urls, result, 'P1651', 'YouTube', 'https://www.youtube.com/watch?v=')
    add_url(urls, result, 'P2002', 'Twitter', 'https://twitter.com/')
    add_url(urls, result, 'P2013', 'Facebook', 'https://facebook.com/')
    add_url(urls, result, 'P2003', 'Instagram', 'https://instagram.com/')

    urls.append({'title': 'Wikidata',
                 'url': 'https://www.wikidata.org/wiki/'
                 + wikidata_id + '?uselang=' + language})

    # INFOBOX ATTRIBUTES (ROWS)

    # DATES
    # inception date
    add_attribute(attributes, result, 'P571', date=True)
    # dissolution date
    add_attribute(attributes, result, 'P576', date=True)
    # start date
    add_attribute(attributes, result, 'P580', date=True)
    # end date
    add_attribute(attributes, result, 'P582', date=True)
    # date of birth
    add_attribute(attributes, result, 'P569', date=True)
    # date of death
    add_attribute(attributes, result, 'P570', date=True)
    # date of spacecraft launch
    add_attribute(attributes, result, 'P619', date=True)
    # date of spacecraft landing
    add_attribute(attributes, result, 'P620', date=True)

    # nationality
    add_attribute(attributes, result, 'P27')
    # country of origin
    add_attribute(attributes, result, 'P495')
    # country
    add_attribute(attributes, result, 'P17')
    # headquarters
    add_attribute(attributes, result, 'Q180')

    # PLACES
    # capital
    add_attribute(attributes, result, 'P36', trim=True)
    # head of state
    add_attribute(attributes, result, 'P35', trim=True)
    # head of government
    add_attribute(attributes, result, 'P6', trim=True)
    # type of government
    add_attribute(attributes, result, 'P122')
    # official language
    add_attribute(attributes, result, 'P37')
    # population
    add_attribute(attributes, result, 'P1082', trim=True)
    # area
    add_attribute(attributes, result, 'P2046')
    # currency
    add_attribute(attributes, result, 'P38', trim=True)
    # heigth (building)
    add_attribute(attributes, result, 'P2048')

    # MEDIA
    # platform (videogames)
    add_attribute(attributes, result, 'P400')
    # author
    add_attribute(attributes, result, 'P50')
    # creator
    add_attribute(attributes, result, 'P170')
    # director
    add_attribute(attributes, result, 'P57')
    # performer
    add_attribute(attributes, result, 'P175')
    # developer
    add_attribute(attributes, result, 'P178')
    # producer
    add_attribute(attributes, result, 'P162')
    # manufacturer
    add_attribute(attributes, result, 'P176')
    # screenwriter
    add_attribute(attributes, result, 'P58')
    # production company
    add_attribute(attributes, result, 'P272')
    # record label
    add_attribute(attributes, result, 'P264')
    # publisher
    add_attribute(attributes, result, 'P123')
    # original network
    add_attribute(attributes, result, 'P449')
    # distributor
    add_attribute(attributes, result, 'P750')
    # composer
    add_attribute(attributes, result, 'P86')
    # publication date
    add_attribute(attributes, result, 'P577', date=True)
    # genre
    add_attribute(attributes, result, 'P136')
    # original language
    add_attribute(attributes, result, 'P364')
    # isbn
    add_attribute(attributes, result, 'Q33057')
    # software license
    add_attribute(attributes, result, 'P275')
    # programming language
    add_attribute(attributes, result, 'P277')
    # version
    add_attribute(attributes, result, 'P348', trim=True)
    # narrative location
    add_attribute(attributes, result, 'P840')

    # LANGUAGES
    # number of speakers
    add_attribute(attributes, result, 'P1098')
    # writing system
    add_attribute(attributes, result, 'P282')
    # regulatory body
    add_attribute(attributes, result, 'P1018')
    # language code
    add_attribute(attributes, result, 'P218')

    # OTHER
    # ceo
    add_attribute(attributes, result, 'P169', trim=True)
    # founder
    add_attribute(attributes, result, 'P112')
    # legal form (company/organization)
    add_attribute(attributes, result, 'P1454')
    # operator
    add_attribute(attributes, result, 'P137')
    # crew members (tripulation)
    add_attribute(attributes, result, 'P1029')
    # taxon
    add_attribute(attributes, result, 'P225')
    # chemical formula
    add_attribute(attributes, result, 'P274')
    # winner (sports/contests)
    add_attribute(attributes, result, 'P1346')
    # number of deaths
    add_attribute(attributes, result, 'P1120')
    # currency code
    add_attribute(attributes, result, 'P498')

    image = add_image(result)

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
                       'img_src': image,
                       'attributes': attributes,
                       'urls': urls
                       })

    return results


# only returns first match
def add_image(result):
    # P15: route map, P242: locator map, P154: logo, P18: image, P242: map, P41: flag, P2716: collage, P2910: icon
    property_ids = ['P15', 'P242', 'P154', 'P18', 'P242', 'P41', 'P2716', 'P2910']

    for property_id in property_ids:
        image = result.xpath(property_xpath.replace('{propertyid}', property_id))
        if image:
            image_name = image[0].xpath(value_xpath)
            image_src = url_image.replace('{filename}', extract_text(image_name[0]))
            return image_src


# setting trim will only returned high ranked rows OR the first row
def add_attribute(attributes, result, property_id, default_label=None, date=False, trim=False):
    attribute = result.xpath(property_xpath.replace('{propertyid}', property_id))
    if attribute:

        if default_label:
            label = default_label
        else:
            label = extract_text(attribute[0].xpath(label_xpath))
            label = label[0].upper() + label[1:]

        if date:
            trim = True
            # remove calendar name
            calendar_name = attribute[0].xpath(calendar_name_xpath)
            for calendar in calendar_name:
                calendar.getparent().remove(calendar)

        concat_values = ""
        values = []
        first_value = None
        for row in attribute[0].xpath(property_row_xpath):
            if not first_value or not trim or row.xpath(preferred_rank_xpath):

                value = row.xpath(value_xpath)
                if not value:
                    continue
                value = extract_text(value)

                # save first value in case no ranked row is found
                if trim and not first_value:
                    first_value = value
                else:
                    # to avoid duplicate values
                    if value not in values:
                        concat_values += value + ", "
                        values.append(value)

        if trim and not values:
            attributes.append({'label': label,
                               'value': first_value})
        else:
            attributes.append({'label': label,
                               'value': concat_values[:-2]})


# requires property_id unless it's a wiki link (defined in link_type)
def add_url(urls, result, property_id=None, default_label=None, url_prefix=None, results=None, link_type=None):
    links = []

    # wiki links don't have property in wikidata page
    if link_type and 'wiki' in link_type:
            links.append(get_wikilink(result, link_type))
    else:
        dom_element = result.xpath(property_xpath.replace('{propertyid}', property_id))
        if dom_element:
            dom_element = dom_element[0]
            if not default_label:
                label = extract_text(dom_element.xpath(label_xpath))
                label = label[0].upper() + label[1:]

            if link_type == 'geo':
                links.append(get_geolink(dom_element))

            elif link_type == 'imdb':
                links.append(get_imdblink(dom_element, url_prefix))

            else:
                url_results = dom_element.xpath(url_xpath)
                for link in url_results:
                    if link is not None:
                        if url_prefix:
                            link = url_prefix + extract_text(link)
                        else:
                            link = extract_text(link)
                        links.append(link)

    # append urls
    for url in links:
        if url is not None:
            urls.append({'title': default_label or label,
                         'url': url})
            if results is not None:
                results.append({'title': default_label or label,
                                'url': url})


def get_imdblink(result, url_prefix):
    imdb_id = result.xpath(value_xpath)
    if imdb_id:
        imdb_id = extract_text(imdb_id)
        id_prefix = imdb_id[:2]
        if id_prefix == 'tt':
            url = url_prefix + 'title/' + imdb_id
        elif id_prefix == 'nm':
            url = url_prefix + 'name/' + imdb_id
        elif id_prefix == 'ch':
            url = url_prefix + 'character/' + imdb_id
        elif id_prefix == 'co':
            url = url_prefix + 'company/' + imdb_id
        elif id_prefix == 'ev':
            url = url_prefix + 'event/' + imdb_id
        else:
            url = None
        return url


def get_geolink(result):
    coordinates = result.xpath(value_xpath)
    if not coordinates:
        return None
    coordinates = extract_text(coordinates[0])
    latitude, longitude = coordinates.split(',')

    # convert to decimal
    lat = int(latitude[:latitude.find(u'°')])
    if latitude.find('\'') >= 0:
        lat += int(latitude[latitude.find(u'°') + 1:latitude.find('\'')] or 0) / 60.0
    if latitude.find('"') >= 0:
        lat += float(latitude[latitude.find('\'') + 1:latitude.find('"')] or 0) / 3600.0
    if latitude.find('S') >= 0:
        lat *= -1
    lon = int(longitude[:longitude.find(u'°')])
    if longitude.find('\'') >= 0:
        lon += int(longitude[longitude.find(u'°') + 1:longitude.find('\'')] or 0) / 60.0
    if longitude.find('"') >= 0:
        lon += float(longitude[longitude.find('\'') + 1:longitude.find('"')] or 0) / 3600.0
    if longitude.find('W') >= 0:
        lon *= -1

    # TODO: get precision
    precision = 0.0002
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
        .replace('{latitude}', str(lat))\
        .replace('{longitude}', str(lon))\
        .replace('{zoom}', str(zoom))

    return url


def get_wikilink(result, wikiid):
    url = result.xpath(wikilink_xpath.replace('{wikiid}', wikiid))
    if not url:
        return None
    url = url[0]
    if url.startswith('http://'):
        url = url.replace('http://', 'https://')
    elif url.startswith('//'):
        url = 'https:' + url
    return url
