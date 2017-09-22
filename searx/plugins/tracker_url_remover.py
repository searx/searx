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
from searx.url_utils import urlunparse

regexes = {re.compile(r'utm_[^&]+&?'),
           re.compile(r'(wkey|wemail)[^&]+&?'),
           re.compile(r'&$')}

name = gettext('Tracker URL remover')
description = gettext('Remove trackers arguments from the returned URL')
default_on = True
preference_section = 'privacy'


def on_result(request, search, result):
    query = result['parsed_url'].query

    if query == "":
        return True

    for reg in regexes:
        query = reg.sub('', query)

    if query != result['parsed_url'].query:
        result['parsed_url'] = result['parsed_url']._replace(query=query)
        result['url'] = urlunparse(result['parsed_url'])

    return True
