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
from flask.ext.babel import gettext
import re
name = "Self User Agent"
description = gettext('Display your own User Agent if the query expression contains "user agent" or "user-agent"')
default_on = True


# User Agent query regex
p = re.compile('user[ -]agent', re.IGNORECASE)


# attach callback to the post search hook
#  request: flask request object
#  ctx: the whole local context of the pre search hook
def post_search(request, ctx):
    if p.match(ctx['search'].query):
        ua = request.user_agent
        ctx['search'].answers.clear()
        ctx['search'].answers.add(ua)
    return True
