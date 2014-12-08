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
from searx.engines.xpath import extract_text, extract_url

# engine dependent config
categories = ['general']
paging = True
language_support = True

# search-url
google_hostname = 'www.google.com'
search_path = '/search'
redirect_path = '/url'
images_path = '/images'
search_url = ('https://' +
              google_hostname +
              search_path +
              '?{query}&start={offset}&gbv=1')

# specific xpath variables
results_xpath = '//li[@class="g"]'
url_xpath = './/h3/a/@href'
title_xpath = './/h3'
content_xpath = './/span[@class="st"]'
suggestion_xpath = '//p[@class="_Bmc"]'

images_xpath = './/div/a'
image_url_xpath = './@href'
image_img_src_xpath = './img/@src'


# remove google-specific tracking-url
def parse_url(url_string):
    parsed_url = urlparse(url_string)
    if (parsed_url.netloc in [google_hostname, '']
            and parsed_url.path == redirect_path):
        query = dict(parse_qsl(parsed_url.query))
        return query['q']
    else:
        return url_string


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10

    if params['language'] == 'all':
        language = 'en'
    else:
        language = params['language'].replace('_', '-').lower()

    params['url'] = search_url.format(offset=offset,
                                      query=urlencode({'q': query}))

    params['headers']['Accept-Language'] = language

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(results_xpath):
        title = extract_text(result.xpath(title_xpath)[0])
        try:
            url = parse_url(extract_url(result.xpath(url_xpath), search_url))
            parsed_url = urlparse(url)
            if (parsed_url.netloc == google_hostname
                    and parsed_url.path == search_path):
                # remove the link to google news
                continue

            # images result
            if (parsed_url.netloc == google_hostname
                    and parsed_url.path == images_path):
                # only thumbnail image provided,
                # so skipping image results
                # results = results + parse_images(result)
                pass
            else:
                # normal result
                content = extract_text(result.xpath(content_xpath)[0])
                # append result
                results.append({'url': url,
                                'title': title,
                                'content': content})
        except:
            continue

    # parse suggestion
    for suggestion in dom.xpath(suggestion_xpath):
        # append suggestion
        results.append({'suggestion': extract_text(suggestion)})

    # return results
    return results


def parse_images(result):
    results = []
    for image in result.xpath(images_xpath):
        url = parse_url(extract_text(image.xpath(image_url_xpath)[0]))
        img_src = extract_text(image.xpath(image_img_src_xpath)[0])

        # append result
        results.append({'url': url,
                        'title': '',
                        'content': '',
                        'img_src': img_src,
                        'template': 'images.html'})

    return results
