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

from searx import settings
from searx.url_utils import urlunparse

name = gettext('Alternate Twitter Frontend')
description = gettext('Open twitter links in alternate frontends like nitter.net')
default_on = False
preference_section = 'privacy'

alternate_domain = settings['rewrite_domains']['twitter']


def on_result(request, search, result):
    if 'parsed_url' not in result:
        return True

    domain = result['parsed_url'].netloc
    if domain == "twitter.com":
        result['parsed_url'] = result['parsed_url']._replace(netloc=alternate_domain)
        result['url'] = urlunparse(result['parsed_url'])
    return True
