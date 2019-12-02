#  Google (Web)
#
# @website     https://www.google.com
# @provide-api yes (https://developers.google.com/custom-search/)
#
# @using-api   no
# @results     HTML
# @stable      no (HTML can change)
# @parse       url, title, content, suggestion

import re
from flask_babel import gettext
from lxml import html, etree
from searx.engines.xpath import extract_text, extract_url
from searx import logger
from searx.url_utils import urlencode, urlparse, parse_qsl
from searx.utils import match_language, eval_xpath

logger = logger.getChild('google engine')


# engine dependent config
categories = ['general']
paging = True
language_support = True
use_locale_domain = True
time_range_support = True

# based on https://en.wikipedia.org/wiki/List_of_Google_domains and tests
default_hostname = 'www.google.com'

country_to_hostname = {
    'BG': 'www.google.bg',  # Bulgaria
    'CZ': 'www.google.cz',  # Czech Republic
    'DE': 'www.google.de',  # Germany
    'DK': 'www.google.dk',  # Denmark
    'AT': 'www.google.at',  # Austria
    'CH': 'www.google.ch',  # Switzerland
    'GR': 'www.google.gr',  # Greece
    'AU': 'www.google.com.au',  # Australia
    'CA': 'www.google.ca',  # Canada
    'GB': 'www.google.co.uk',  # United Kingdom
    'ID': 'www.google.co.id',  # Indonesia
    'IE': 'www.google.ie',  # Ireland
    'IN': 'www.google.co.in',  # India
    'MY': 'www.google.com.my',  # Malaysia
    'NZ': 'www.google.co.nz',  # New Zealand
    'PH': 'www.google.com.ph',  # Philippines
    'SG': 'www.google.com.sg',  # Singapore
    # 'US': 'www.google.us',  # United States, redirect to .com
    'ZA': 'www.google.co.za',  # South Africa
    'AR': 'www.google.com.ar',  # Argentina
    'CL': 'www.google.cl',  # Chile
    'ES': 'www.google.es',  # Spain
    'MX': 'www.google.com.mx',  # Mexico
    'EE': 'www.google.ee',  # Estonia
    'FI': 'www.google.fi',  # Finland
    'BE': 'www.google.be',  # Belgium
    'FR': 'www.google.fr',  # France
    'IL': 'www.google.co.il',  # Israel
    'HR': 'www.google.hr',  # Croatia
    'HU': 'www.google.hu',  # Hungary
    'IT': 'www.google.it',  # Italy
    'JP': 'www.google.co.jp',  # Japan
    'KR': 'www.google.co.kr',  # South Korea
    'LT': 'www.google.lt',  # Lithuania
    'LV': 'www.google.lv',  # Latvia
    'NO': 'www.google.no',  # Norway
    'NL': 'www.google.nl',  # Netherlands
    'PL': 'www.google.pl',  # Poland
    'BR': 'www.google.com.br',  # Brazil
    'PT': 'www.google.pt',  # Portugal
    'RO': 'www.google.ro',  # Romania
    'RU': 'www.google.ru',  # Russia
    'SK': 'www.google.sk',  # Slovakia
    'SI': 'www.google.si',  # Slovenia
    'SE': 'www.google.se',  # Sweden
    'TH': 'www.google.co.th',  # Thailand
    'TR': 'www.google.com.tr',  # Turkey
    'UA': 'www.google.com.ua',  # Ukraine
    # 'CN': 'www.google.cn',  # China, only from China ?
    'HK': 'www.google.com.hk',  # Hong Kong
    'TW': 'www.google.com.tw'  # Taiwan
}

# osm
url_map = 'https://www.openstreetmap.org/'\
    + '?lat={latitude}&lon={longitude}&zoom={zoom}&layers=M'

# search-url
search_path = '/search'
search_url = ('https://{hostname}' +
              search_path +
              '?{query}&start={offset}&gws_rd=cr&gbv=1&lr={lang}&hl={lang_short}&ei=x')

time_range_search = "&tbs=qdr:{range}"
time_range_dict = {'day': 'd',
                   'week': 'w',
                   'month': 'm',
                   'year': 'y'}

# other URLs
map_hostname_start = 'maps.google.'
maps_path = '/maps'
redirect_path = '/url'
images_path = '/images'
supported_languages_url = 'https://www.google.com/preferences?#languages'

# specific xpath variables
results_xpath = '//div[@class="g"]'
url_xpath = './/h3/a/@href'
title_xpath = './/h3'
content_xpath = './/span[@class="st"]'
content_misc_xpath = './/div[@class="f slp"]'
suggestion_xpath = '//p[@class="_Bmc"]'
spelling_suggestion_xpath = '//a[@class="spell"]'

# map : detail location
map_address_xpath = './/div[@class="s"]//table//td[2]/span/text()'
map_phone_xpath = './/div[@class="s"]//table//td[2]/span/span'
map_website_url_xpath = 'h3[2]/a/@href'
map_website_title_xpath = 'h3[2]'

# map : near the location
map_near = 'table[@class="ts"]//tr'
map_near_title = './/h4'
map_near_url = './/h4/a/@href'
map_near_phone = './/span[@class="nobr"]'

# images
images_xpath = './/div/a'
image_url_xpath = './@href'
image_img_src_xpath = './img/@src'

# property names
# FIXME : no translation
property_address = "Address"
property_phone = "Phone number"


# remove google-specific tracking-url
def parse_url(url_string, google_hostname):
    # sanity check
    if url_string is None:
        return url_string

    # normal case
    parsed_url = urlparse(url_string)
    if (parsed_url.netloc in [google_hostname, '']
            and parsed_url.path == redirect_path):
        query = dict(parse_qsl(parsed_url.query))
        return query['q']
    else:
        return url_string


# returns extract_text on the first result selected by the xpath or None
def extract_text_from_dom(result, xpath):
    r = eval_xpath(result, xpath)
    if len(r) > 0:
        return extract_text(r[0])
    return None


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10

    if params['language'] == 'all' or params['language'] == 'en-US':
        language = 'en-GB'
    else:
        language = match_language(params['language'], supported_languages, language_aliases)

    language_array = language.split('-')
    if params['language'].find('-') > 0:
        country = params['language'].split('-')[1]
    elif len(language_array) == 2:
        country = language_array[1]
    else:
        country = 'US'

    url_lang = 'lang_' + language

    if use_locale_domain:
        google_hostname = country_to_hostname.get(country.upper(), default_hostname)
    else:
        google_hostname = default_hostname

    # original format: ID=3e2b6616cee08557:TM=5556667580:C=r:IP=4.1.12.5-:S=23ASdf0soFgF2d34dfgf-_22JJOmHdfgg
    params['cookies']['GOOGLE_ABUSE_EXEMPTION'] = 'x'
    params['url'] = search_url.format(offset=offset,
                                      query=urlencode({'q': query}),
                                      hostname=google_hostname,
                                      lang=url_lang,
                                      lang_short=language)
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_search.format(range=time_range_dict[params['time_range']])

    params['headers']['Accept-Language'] = language + ',' + language + '-' + country
    params['headers']['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

    # Force Safari 3.1 on Mac OS X (Leopard) user agent to avoid loading the new UI that Searx can't parse
    params['headers']['User-Agent'] = ("Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_4)"
                                       "AppleWebKit/525.18 (KHTML, like Gecko) Version/3.1.2 Safari/525.20.1")

    params['google_hostname'] = google_hostname

    return params


# get response from search-request
def response(resp):
    results = []

    # detect google sorry
    resp_url = urlparse(resp.url)
    if resp_url.netloc == 'sorry.google.com' or resp_url.path == '/sorry/IndexRedirect':
        raise RuntimeWarning('sorry.google.com')

    if resp_url.path.startswith('/sorry'):
        raise RuntimeWarning(gettext('CAPTCHA required'))

    # which hostname ?
    google_hostname = resp.search_params.get('google_hostname')
    google_url = "https://" + google_hostname

    # convert the text to dom
    dom = html.fromstring(resp.text)

    instant_answer = eval_xpath(dom, '//div[@id="_vBb"]//text()')
    if instant_answer:
        results.append({'answer': u' '.join(instant_answer)})
    try:
        results_num = int(eval_xpath(dom, '//div[@id="resultStats"]//text()')[0]
                          .split()[1].replace(',', ''))
        results.append({'number_of_results': results_num})
    except:
        pass

    # parse results
    for result in eval_xpath(dom, results_xpath):
        try:
            title = extract_text(eval_xpath(result, title_xpath)[0])
            url = parse_url(extract_url(eval_xpath(result, url_xpath), google_url), google_hostname)
            parsed_url = urlparse(url, google_hostname)

            # map result
            if parsed_url.netloc == google_hostname:
                # TODO fix inside links
                continue
                # if parsed_url.path.startswith(maps_path) or parsed_url.netloc.startswith(map_hostname_start):
                #     print "yooooo"*30
                #     x = eval_xpath(result, map_near)
                #     if len(x) > 0:
                #         # map : near the location
                #         results = results + parse_map_near(parsed_url, x, google_hostname)
                #     else:
                #         # map : detail about a location
                #         results = results + parse_map_detail(parsed_url, result, google_hostname)
                # # google news
                # elif parsed_url.path == search_path:
                #     # skipping news results
                #     pass

                # # images result
                # elif parsed_url.path == images_path:
                #     # only thumbnail image provided,
                #     # so skipping image results
                #     # results = results + parse_images(result, google_hostname)
                #     pass

            else:
                # normal result
                content = extract_text_from_dom(result, content_xpath)
                if content is None:
                    continue
                content_misc = extract_text_from_dom(result, content_misc_xpath)
                if content_misc is not None:
                    content = content_misc + "<br />" + content
                # append result
                results.append({'url': url,
                                'title': title,
                                'content': content
                                })
        except:
            logger.debug('result parse error in:\n%s', etree.tostring(result, pretty_print=True))
            continue

    # parse suggestion
    for suggestion in eval_xpath(dom, suggestion_xpath):
        # append suggestion
        results.append({'suggestion': extract_text(suggestion)})

    for correction in eval_xpath(dom, spelling_suggestion_xpath):
        results.append({'correction': extract_text(correction)})

    # return results
    return results


def parse_images(result, google_hostname):
    results = []
    for image in eval_xpath(result, images_xpath):
        url = parse_url(extract_text(eval_xpath(image, image_url_xpath)[0]), google_hostname)
        img_src = extract_text(eval_xpath(image, image_img_src_xpath)[0])

        # append result
        results.append({'url': url,
                        'title': '',
                        'content': '',
                        'img_src': img_src,
                        'template': 'images.html'
                        })

    return results


def parse_map_near(parsed_url, x, google_hostname):
    results = []

    for result in x:
        title = extract_text_from_dom(result, map_near_title)
        url = parse_url(extract_text_from_dom(result, map_near_url), google_hostname)
        attributes = []
        phone = extract_text_from_dom(result, map_near_phone)
        add_attributes(attributes, property_phone, phone, 'tel:' + phone)
        results.append({'title': title,
                        'url': url,
                        'content': attributes_to_html(attributes)
                        })

    return results


def parse_map_detail(parsed_url, result, google_hostname):
    results = []

    # try to parse the geoloc
    m = re.search(r'@([0-9\.]+),([0-9\.]+),([0-9]+)', parsed_url.path)
    if m is None:
        m = re.search(r'll\=([0-9\.]+),([0-9\.]+)\&z\=([0-9]+)', parsed_url.query)

    if m is not None:
        # geoloc found (ignored)
        lon = float(m.group(2))  # noqa
        lat = float(m.group(1))  # noqa
        zoom = int(m.group(3))  # noqa

        # attributes
        attributes = []
        address = extract_text_from_dom(result, map_address_xpath)
        phone = extract_text_from_dom(result, map_phone_xpath)
        add_attributes(attributes, property_address, address, 'geo:' + str(lat) + ',' + str(lon))
        add_attributes(attributes, property_phone, phone, 'tel:' + phone)

        # title / content / url
        website_title = extract_text_from_dom(result, map_website_title_xpath)
        content = extract_text_from_dom(result, content_xpath)
        website_url = parse_url(extract_text_from_dom(result, map_website_url_xpath), google_hostname)

        # add a result if there is a website
        if website_url is not None:
            results.append({'title': website_title,
                            'content': (content + '<br />' if content is not None else '')
                            + attributes_to_html(attributes),
                            'url': website_url
                            })

    return results


def add_attributes(attributes, name, value, url):
    if value is not None and len(value) > 0:
        attributes.append({'label': name, 'value': value, 'url': url})


def attributes_to_html(attributes):
    retval = '<table class="table table-striped">'
    for a in attributes:
        value = a.get('value')
        if 'url' in a:
            value = '<a href="' + a.get('url') + '">' + value + '</a>'
        retval = retval + '<tr><th>' + a.get('label') + '</th><td>' + value + '</td></tr>'
    retval = retval + '</table>'
    return retval


# get supported languages from their site
def _fetch_supported_languages(resp):
    supported_languages = {}
    dom = html.fromstring(resp.text)
    options = eval_xpath(dom, '//*[@id="langSec"]//input[@name="lr"]')
    for option in options:
        code = eval_xpath(option, './@value')[0].split('_')[-1]
        name = eval_xpath(option, './@data-name')[0].title()
        supported_languages[code] = {"name": name}

    return supported_languages
