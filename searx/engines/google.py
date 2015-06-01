#  Google (Web)
#
# @website     https://www.google.com
# @provide-api yes (https://developers.google.com/custom-search/)
#
# @using-api   no
# @results     HTML
# @stable      no (HTML can change)
# @parse       url, title, content, suggestion

from urllib import urlencode
from urlparse import urlparse, parse_qsl
from lxml import html
from searx.poolrequests import get
from searx.engines.xpath import extract_text, extract_url


# engine dependent config
categories = ['general']
paging = True
language_support = True
use_locale_domain = True

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
    # 'US': 'www.google.us',  # United State, redirect to .com
    'ZA': 'www.google.co.za',  # South Africa
    'AR': 'www.google.com.ar',  # Argentina
    'CL': 'www.google.cl',  # Chile
    'ES': 'www.google.es',  # Span
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
    'KR': 'www.google.co.kr',  # South Korean
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
    'SL': 'www.google.si',  # Slovenia (SL -> si)
    'SE': 'www.google.se',  # Sweden
    'TH': 'www.google.co.th',  # Thailand
    'TR': 'www.google.com.tr',  # Turkey
    'UA': 'www.google.com.ua',  # Ikraine
    # 'CN': 'www.google.cn',  # China, only from china ?
    'HK': 'www.google.com.hk',  # Hong kong
    'TW': 'www.google.com.tw'  # Taiwan
}

# search-url
search_path = '/search'
maps_path = '/maps/'
redirect_path = '/url'
images_path = '/images'
search_url = ('https://{hostname}' +
              search_path +
              '?{query}&start={offset}&gbv=1')

# specific xpath variables
results_xpath = '//li[@class="g"]'
url_xpath = './/h3/a/@href'
title_xpath = './/h3'
content_xpath = './/span[@class="st"]'
content_misc_xpath = './/div[@class="f slp"]'
suggestion_xpath = '//p[@class="_Bmc"]'

images_xpath = './/div/a'
image_url_xpath = './@href'
image_img_src_xpath = './img/@src'

pref_cookie = ''
nid_cookie = {}


# see https://support.google.com/websearch/answer/873?hl=en
def get_google_pref_cookie():
    global pref_cookie
    if pref_cookie == '':
        resp = get('https://www.google.com/ncr', allow_redirects=False)
        pref_cookie = resp.cookies["PREF"]
    return pref_cookie


def get_google_nid_cookie(google_hostname):
    global nid_cookie
    if google_hostname not in nid_cookie:
        resp = get('https://' + google_hostname)
        nid_cookie[google_hostname] = resp.cookies.get("NID", None)
    return nid_cookie[google_hostname]


# remove google-specific tracking-url
def parse_url(url_string, google_hostname):
    parsed_url = urlparse(url_string)
    if (parsed_url.netloc in [google_hostname, '']
            and parsed_url.path == redirect_path):
        query = dict(parse_qsl(parsed_url.query))
        return query['q']
    else:
        return url_string


# returns extract_text on the first result selected by the xpath or None
def extract_text_from_dom(result, xpath):
    r = result.xpath(xpath)
    if len(r) > 0:
        return extract_text(r[0])
    return None


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10

    if params['language'] == 'all':
        language = 'en'
        country = 'US'
    else:
        language_array = params['language'].lower().split('_')
        if len(language_array) == 2:
            country = language_array[1]
        else:
            country = '  '
        language = language_array[0] + ',' + language_array[0] + '-' + country

    if use_locale_domain:
        google_hostname = country_to_hostname.get(country.upper(), default_hostname)
    else:
        google_hostname = default_hostname

    params['url'] = search_url.format(offset=offset,
                                      query=urlencode({'q': query}),
                                      hostname=google_hostname)

    params['headers']['Accept-Language'] = language
    params['headers']['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    if google_hostname == default_hostname:
        params['cookies']['PREF'] = get_google_pref_cookie()
    params['cookies']['NID'] = get_google_nid_cookie(google_hostname)

    params['google_hostname'] = google_hostname

    return params


# get response from search-request
def response(resp):
    results = []

    # detect google sorry
    resp_url = urlparse(resp.url)
    if resp_url.netloc == 'sorry.google.com' or resp_url.path == '/sorry/IndexRedirect':
        raise RuntimeWarning('sorry.google.com')

    # which hostname ?
    google_hostname = resp.search_params.get('google_hostname')
    google_url = "https://" + google_hostname

    # convert the text to dom
    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(results_xpath):
        title = extract_text(result.xpath(title_xpath)[0])
        try:
            url = parse_url(extract_url(result.xpath(url_xpath), google_url), google_hostname)
            parsed_url = urlparse(url, google_hostname)
            if (parsed_url.netloc == google_hostname
                and (parsed_url.path == search_path
                     or parsed_url.path.startswith(maps_path))):
                # remove the link to google news and google maps
                # FIXME : sometimes the URL is https://maps.google.*/maps
                # no consequence, the result trigger an exception after which is ignored
                continue

            # images result
            if (parsed_url.netloc == google_hostname
                    and parsed_url.path == images_path):
                # only thumbnail image provided,
                # so skipping image results
                # results = results + parse_images(result, google_hostname)
                pass
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
                                'content': content})
        except Exception:
            continue

    # parse suggestion
    for suggestion in dom.xpath(suggestion_xpath):
        # append suggestion
        results.append({'suggestion': extract_text(suggestion)})

    # return results
    return results


def parse_images(result, google_hostname):
    results = []
    for image in result.xpath(images_xpath):
        url = parse_url(extract_text(image.xpath(image_url_xpath)[0]), google_hostname)
        img_src = extract_text(image.xpath(image_img_src_xpath)[0])

        # append result
        results.append({'url': url,
                        'title': '',
                        'content': '',
                        'img_src': img_src,
                        'template': 'images.html'})

    return results
