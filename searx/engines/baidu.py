# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Baidu
"""

from json import loads
from urllib.parse import urlencode, urlparse
from bs4 import BeautifulSoup
from searx.exceptions import SearxEngineException
#import requests
# about
about = {
    "website": 'https://github.com/',
    "wikidata_id": 'Q14772',
    "use_official_api": False,
    "require_api_key": False,
    "results": 'JSON',
}

# engine dependent config
categories = ['general']

# search-url
baidu_host_url = "https://www.baidu.com"
baidu_search_url = "https://www.baidu.com/s?ie=utf-8&tn=baidu&{query}"

ABSTRACT_MAX_LENGTH = 500


# do search-request
def request(query, params):

    offset = (params['pageno'] - 1) * 10
    params['url'] = baidu_search_url.format(query=urlencode({
        'wd': query,
        'pn': offset
    }))
    # headers
    params['headers']['Accept'] = (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    )
    params['headers']['Accept-Language'] = ("zh-CN,zh;q=0.9")
    params['headers']['Content-Type'] = ("application/x-www-form-urlencoded")
    params['headers']['User-Agent'] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
    )
    params['headers']['Accept-Encoding'] = ("gzip, deflate")
    params['headers']['Referer'] = ("https://www.baidu.com/")

    return params


# get response from search-request
def response(resp):
    results = []
    try:
        resp.encoding = "utf-8"
        root = BeautifulSoup(resp.text, "lxml")
        div_contents = root.find("div", id="content_left")
        for div in div_contents.contents:
            if type(div) != type(div_contents):
                continue

            class_list = div.get("class", [])
            if not class_list:
                continue

            if "c-container" not in class_list:
                continue

            title = ''
            url = ''
            abstract = ''
            if "xpath-log" in class_list:
                if div.h3:
                    title = div.h3.text.strip()
                    url = div.h3.a['href'].strip()
                else:
                    title = div.text.strip().split("\n", 1)[0]
                    if div.a:
                        url = div.a['href'].strip()

                if div.find("div", class_="c-abstract"):
                    abstract = div.find("div",
                                        class_="c-abstract").text.strip()
                elif div.div:
                    abstract = div.div.text.strip()
                else:
                    abstract = div.text.strip().split("\n", 1)[1].strip()
            elif "result-op" in class_list:
                if div.h3:
                    title = div.h3.text.strip()
                    url = div.h3.a['href'].strip()
                else:
                    title = div.text.strip().split("\n", 1)[0]
                    url = div.a['href'].strip()
                if div.find("div", class_="c-abstract"):
                    abstract = div.find("div",
                                        class_="c-abstract").text.strip()
                elif div.div:
                    abstract = div.div.text.strip()
                else:
                    # abstract = div.text.strip()
                    abstract = div.text.strip().split("\n", 1)[1].strip()
            else:
                if div.get("tpl", "") != "se_com_default":
                    if div.get("tpl", "") == "se_st_com_abstract":
                        if len(div.contents) >= 1:
                            title = div.h3.text.strip()
                            if div.find("div", class_="c-abstract"):
                                abstract = div.find(
                                    "div", class_="c-abstract").text.strip()
                            elif div.div:
                                abstract = div.div.text.strip()
                            else:
                                abstract = div.text.strip()
                    else:
                        if len(div.contents) >= 2:
                            if div.h3:
                                title = div.h3.text.strip()
                                url = div.h3.a['href'].strip()
                            else:
                                title = div.contents[0].text.strip()
                                url = div.h3.a['href'].strip()
                            # abstract = div.contents[-1].text
                            if div.find("div", class_="c-abstract"):
                                abstract = div.find(
                                    "div", class_="c-abstract").text.strip()
                            elif div.div:
                                abstract = div.div.text.strip()
                            else:
                                abstract = div.text.strip()
                else:
                    if div.h3:
                        title = div.h3.text.strip()
                        url = div.h3.a['href'].strip()
                    else:
                        title = div.contents[0].text.strip()
                        url = div.h3.a['href'].strip()
                    if div.find("div", class_="c-abstract"):
                        abstract = div.find("div",
                                            class_="c-abstract").text.strip()
                    elif div.div:
                        abstract = div.div.text.strip()
                    else:
                        abstract = div.text.strip()

            if ABSTRACT_MAX_LENGTH and len(abstract) > ABSTRACT_MAX_LENGTH:
                abstract = abstract[:ABSTRACT_MAX_LENGTH]
            #re = requests.Session.get(url, allow_redirects=False)
            #url = re.headers['location']
            # append result
            results.append({'url': url, 'title': title, 'content': abstract})
    except Exception as e:
        raise SearxEngineException()
    # return results
    return results
