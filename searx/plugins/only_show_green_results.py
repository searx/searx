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

name = gettext('Only show green hosted results')
description = gettext('Any results not being hosted on green infrastructure will be filtered')
default_on = True
preference_section = 'privacy'

# attach callback to the post search hook
#  request: flask request object
#  ctx: the whole local context of the pre search hook
def post_search(request, search):
    print search


def on_result(request, search, result):
    if 'parsed_url' not in result:
        return True

    print result['url']

    # Put a green.html template up to have access over which results are shown or not
    # @todo figure out a way to filter results in this callback so we don't need a special template
    result['template'] = 'green.html'

    # @todo hook up the url to our greencheck tool instead of api here
    response = requests.get("https://api.thegreenwebfoundation.org/greencheck/" + result['parsed_url'].netloc)
    data = response.json()
    #print(data['green'])

    result['green'] = data['green']

    return True
