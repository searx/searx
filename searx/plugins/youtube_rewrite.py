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

name = gettext('Alternate Youtube Frontend')
description = gettext('Open youtube video links in alternate frontends like invidio.us')
default_on = False
preference_section = 'privacy'

youtube_pattern = "youtube.com/watch"
alternate_domain = settings['rewrite_domains']['youtube']


def on_result(request, search, result):
    if 'parsed_url' not in result:
        return True

    if youtube_pattern in result['url']:
        result['parsed_url'] = result['parsed_url']._replace(netloc=alternate_domain)
        result['url'] = urlunparse(result['parsed_url'])
    return True
