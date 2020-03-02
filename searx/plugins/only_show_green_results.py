'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2015 by Adam Tauber, <asciimoo@gmail.com>
'''

from flask_babel import gettext
import re
from searx.url_utils import urlunparse, parse_qsl, urlencode
import requests
import logging

import sqlite3
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

name = gettext('Only show green hosted results')
description = gettext('Any results not being hosted on green infrastructure will be filtered')
default_on = True
preference_section = 'privacy'
allow_api_connections = False


class GreenCheck:

    def __init__(self):
        self.conn = None

        try:
            self.conn = sqlite3.connect('url2green.db', check_same_thread=False)
            logger.info("url2green database found. ready for queries")
        except:
            logging.exception('No url2green database found. Falling back to the API')

    def check_url(self, url=None) -> bool:
        """
        Check a url passed in, and return a true or false result,
        based on whether the domain is marked as a one running on
        green energy.
        """
        try:
            parsed_domain = self.get_domain_from_url(url)
        except Exception as e:
            logger.exception(f"unable to parse url: {url}")

        if parsed_domain:
            logger.debug(f"Checking {parsed_domain}, parsed from {url}")

            if self.conn:
                return self.check_in_db(parsed_domain)
            else:
                if allow_api_connections:
                    return self.check_against_api(parsed_domain)
                else:
                    return false

    def get_domain_from_url(self, url=None):
        return urlparse(url).hostname

    def check_in_db(self, domain=None):
        c = self.conn.cursor()
        c.execute("SELECT green FROM green_presenting WHERE url=? LIMIT 1", [domain])
        res = c.fetchone()
        logger.debug(res)
        c.close()
        return bool(res)

    def check_against_api(self, domain=None):
        API_SERVER = "https://api.thegreenwebfoundation.org/"
        response = requests.get(f"{API_SERVER}/greencheck/{domain}").json()
        if response.get(green):
            return True

greencheck = GreenCheck()

# attach callback to the post search hook
#  request: flask request object
#  ctx: the whole local context of the pre search hook
def post_search(request, search):
    logger.debug(search.result_container._merged_results)

    green_results = [
        entry for entry in list(search.result_container._merged_results)
        if get_green(entry)
    ]
    search.result_container._merged_results = green_results
    return True

def get_green(result):
    logger.debug(result.get('url'))
    green = greencheck.check_url(result.get('url'))
    if green:
        return True


