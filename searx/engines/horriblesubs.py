"""
 horriblesubs.info (Anime rips)

 @website      http://horriblesubs.info/
 @provide-api  no
 @using-api    no
 @results      HTML
 @stable       no (HTML can change)
 @parse        title, content, torrentfile, magnetlink, ddls
"""

from cgi import escape
from urllib import urlencode
from lxml import html
from lxml.etree import XMLSyntaxError
from searx.engines.xpath import extract_text

# engine dependent config
categories = ['files', 'videos']
paging = True

# search-url
base_url = 'http://horriblesubs.info/'
search_url = base_url + 'lib/search.php?{query}&nextid={offset}'

# xpath queries
xpath_results = '//div[contains(@class, "release-links")]'
xpath_title = './/td[contains(@class, "dl-label")]/i'
xpath_magnetlink = './/td[contains(@class, "hs-magnet-link")]/span/a'
xpath_torrentfile = './/td[contains(@class, "hs-torrent-link")]/span/a'
xpath_ddls = './/td[contains(@class, "hs-ddl-link")]/span/a'


# do search-request
def request(query, params):
    query = urlencode({'value': query})
    params['url'] = search_url.format(query=query, offset=params['pageno']-1)
    return params


# get response from search-request
def response(resp):
    results = []

    try:
        dom = html.fromstring(resp.text)
    except XMLSyntaxError:
        return results

    for result in dom.xpath(xpath_results):
        title = result.xpath(xpath_title)[0].text_content()
        content = "Resolution: " + title[title.index('[')+1:title.index(']')]

        magnetlink = result.xpath(xpath_magnetlink)[0].attrib.get('href')

        torrentfile = result.xpath(xpath_torrentfile)[0].attrib.get('href')
        href = torrentfile.replace('page=download', 'page=view')

        ddls = []
        for ddl in result.xpath(xpath_ddls):
            ddl_href = ddl.attrib.get('href')
            ddl_title = ddl.text_content()
            ddls.append({'url': ddl_href,
                         'title': ddl_title})

        results.append({'url': href,
                        'title': title,
                        'content': content,
                        'magnetlink': magnetlink,
                        'torrentfile': torrentfile,
                        'ddls': ddls})

    return results
