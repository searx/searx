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
from urllib import urlencode, unquote_plus
from urlparse import urljoin
from lxml import html
from lxml.etree import XMLSyntaxError
import re
from searx.engines.xpath import extract_text
from searx.poolrequests import get as http_get

# engine dependent config
categories = ['files', 'videos']
paging = True

# search-url
base_url = 'http://horriblesubs.info/'
schedules_url = 'http://horriblesubs.info/release-schedule/'
search_url = base_url + 'lib/search.php?{query}&nextid={offset}'

# xpath queries
xpath_results = '//div[contains(@class, "release-links")]'
xpath_title = './/td[contains(@class, "dl-label")]/i'
xpath_magnetlink = './/td[contains(@class, "hs-magnet-link")]/span/a'
xpath_torrentfile = './/td[contains(@class, "hs-torrent-link")]/span/a'
xpath_ddls = './/td[contains(@class, "hs-ddl-link")]/span/a'

xpath_schedule_weekdays = '//h2[contains(@class, "weekday")]'
xpath_schedule_shows = './/tr[contains(@class, "schedule-page-item")]'
xpath_schedule_show_title = './/td[contains(@class, "schedule-page-show")]/a'
xpath_schedule_show_time = './/td[contains(@class, "schedule-time")]'


def index_schedules():
    schedules = []

    resp = http_get(schedules_url)
    dom = html.fromstring(resp.text)

    for weekday in dom.xpath(xpath_schedule_weekdays):
        day = weekday.text_content()

        weekday_table = weekday.getnext()
        shows = []

        for show in weekday_table.xpath(xpath_schedule_shows):
            title = show.xpath(xpath_schedule_show_title)[0]
            href = urljoin(base_url, title.attrib.get('href'))
            title = title.text_content()
            time = show.xpath(xpath_schedule_show_time)[0].text_content()
            shows.append({'title': title,
                          'url': href,
                          'time': time})

        schedules.append({'weekday': day,
                          'shows': shows})

    return schedules

schedules = index_schedules()


# search for a schedule entry
def search_schedule(search):
    search = search.lower()
    results = []

    for weekday in schedules:
        for show in weekday['shows']:
            if search in show['title'].lower():
                result = show
                result['weekday'] = weekday['weekday']
                results.append(result)

    return results


# do search-request
def request(query, params):
    query = urlencode({'value': query})
    params['url'] = search_url.format(query=query, offset=params['pageno'] - 1)
    return params


# get response from search-request
def response(resp):
    results = []

    try:
        query = unquote_plus(re.search(r'value=(.*?)&', resp.url).groups()[0])
    except TypeError:
        pass
    else:
        shows = search_schedule(query)

        for show in shows:
            content = 'Releases at {weekday} {time} PST'
            content = content.format(weekday=show['weekday'], time=show['time'])
            results.append({'url': show['url'],
                            'title': show['title'],
                            'content': content})

    try:
        dom = html.fromstring(resp.text)
    except XMLSyntaxError:
        return results

    for result in dom.xpath(xpath_results):
        title = result.xpath(xpath_title)[0].text_content()
        content = 'Resolution: ' + title[title.index('[') + 1:title.index(']')]

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
