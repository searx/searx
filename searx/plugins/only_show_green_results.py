'''
 SPDX-License-Identifier: AGPL-3.0-or-later
'''

from flask_babel import gettext
import re
from searx.url_utils import urlunparse, parse_qsl, urlencode
import requests
import logging
import os

import sqlite3
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

name = gettext('Only show green hosted results')
description = gettext('Any results not being hosted on green infrastructure will be filtered')
default_on = True
preference_section = 'privacy'
allow_api_connections = True
database_name = "url2green.db"


class GreenCheck:

    def __init__(self):
        try:
            self.db = bool(os.stat(database_name))
            logger.debug(f"Database found at {database_name}. Using it for lookups instead of the Greencheck API")
        except FileNotFoundError:
            self.db = False
            if allow_api_connections:
                logger.debug(f"No database found at {database_name}.")
                logger.debug(f"Falling back to the instead of the Greencheck API, as 'allow_api_connections' is set to {allow_api_connections}.")
            else:
                logger.debug(f"No database found at {database_name}. Not making any checks, because 'allow_api_connections' is set to {allow_api_connections}")


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

            if self.db:
                return self.check_in_db(parsed_domain)
            else:
                if allow_api_connections:
                    return self.check_against_api(parsed_domain)
                else:
                    return False

    def get_domain_from_url(self, url=None):
        return urlparse(url).hostname

    def check_in_db(self, domain=None):

        with sqlite3.connect(database_name) as con:
            cur = con.cursor()
            cur.execute("SELECT green FROM green_presenting WHERE url=? LIMIT 1",
                [domain]
            )
            res = cur.fetchone()
            logger.debug(res)
            return bool(res)

    def check_against_api(self, domain=None):
        api_server = "https://api.thegreenwebfoundation.org"
        api_url = f"{api_server}/greencheck/{domain}"
        logger.debug(api_url)
        response = requests.get(api_url).json()

        if response.get("green"):
            return True

greencheck = GreenCheck()

# attach callback to the post search hook
#  request: flask request object
#  ctx: the whole local context of the pre search hook
def post_search(request, search):
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


