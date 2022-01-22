# SPDX-License-Identifier: AGPL-3.0-or-later

"""
 xPath Flex Engine (xpath_flex)

 Aims to be a more flexible engine that covers xpath use cases for all categories
 (as it allows to override the result template).
 The engine configuration expects you to specify a 'field_definition' dictionary with the following properties:
 * field_name: the template field that should be set by this entry.
 * xpath: a xpath expression to apply
 * (optional) single_element: if True, will execute the xpath expression to expect a single node, not a list
 * (optional) extract: a string specifying an extraction/conversion of the value, the following is supported:
   "url": extracts an url using base search url
   "boolean": will convert the value passed to the template to True if the xpath matches any node
   "boolean_negate": will convert the value passed to the template to True if the xpath does NOT match a node
   by default, text will be extracted from the found node(s)

 an example would look like this (for an example shopping site with paging):

   - name : xpath-flex-example
    engine : xpath_flex
    paging : True
    search_url : https://myl-shopping.site/search?q={query}&p={pageno}
    template : products.html
    results_xpath : //div[@class="listing--container"]/div[@class="listing"]/div[contains(@class,"product--box")]
    field_definition:
      - field_name: url
        xpath: (.//a[contains(@class,"product--image")])/@href
        extract: url
      - field_name: title
        xpath: (.//a[contains(@class,"product--image")])/@title
      - field_name: content
        xpath: .//div[@class="product--description"]/text()
      - field_name: price
        xpath: .//div[@class="product--price"]/span/text()
      - field_name: thumbnail
        xpath: substring-before( (.//span[@class="image--media"]/img)/@srcset, ", ")
        extract: url
        single_element: True
      - field_name: has_stock
        xpath: .//a[contains(@class,"buynow")][not(contains(@class,"is--disabled"))]
        extract: boolean
        single_element: True

"""

from lxml import html
from urllib.parse import urlencode
from searx import logger
from searx.utils import extract_text, extract_url, eval_xpath, eval_xpath_list

logger = logger.getChild('xpath_general engine')

search_url = None
paging = False
results_xpath = ''
soft_max_redirects = 0
template = 'default.html'
unresolvable_value = ''  # will be set if expression cannot be resolved
default_field_settings = {'single_element': False}

field_definition = {}

# parameters for engines with paging support
#
# number of results on each page
# (only needed if the site requires not a page number, but an offset)
page_size = 1
# number of the first page (usually 0 or 1)
first_page_num = 1


def request(query, params):
    query = urlencode({'q': query})[2:]

    fp = {'query': query}
    if paging and search_url.find('{pageno}') >= 0:
        fp['pageno'] = (params['pageno'] - 1) * page_size + first_page_num

    params['url'] = search_url.format(**fp)
    params['query'] = query
    params['soft_max_redirects'] = soft_max_redirects

    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)

    for result in eval_xpath_list(dom, results_xpath):

        single_result = {
            'template': template
        }

        for single_field in field_definition:
            single_field = {**default_field_settings, **single_field}
            try:
                if single_field['single_element']:
                    node = eval_xpath(result, single_field['xpath'])
                else:
                    node = eval_xpath_list(result, single_field['xpath'])

                if 'extract' in single_field and single_field['extract'] == 'url':
                    value = extract_url(node, search_url)
                elif 'extract' in single_field and single_field['extract'] == 'boolean':
                    value = (isinstance(node, list) and len(node) > 0)
                elif 'extract' in single_field and single_field['extract'] == 'boolean_negate':
                    value = (isinstance(node, list) and len(node) < 1)
                else:
                    value = extract_text(node)

                single_result[single_field['field_name']] = value
            except Exception as e:
                logger.warning('error in resolving field %s:\n%s', single_field['field_name'], e)
                single_result[single_field['field_name']] = unresolvable_value

        results.append(single_result)

    return results
