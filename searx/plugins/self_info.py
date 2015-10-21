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
name = "Self Informations"
description = gettext('Displays your IP if the query is "ip" and your user agent if the query contains "user agent".')
default_on = True


# Self User Agent regex
p = re.compile('.*user[ -]agent.*', re.IGNORECASE)


# attach callback to the post search hook
#  request: flask request object
#  ctx: the whole local context of the pre search hook
def post_search(request, ctx):
    if ctx['search'].query == 'ip':
        x_forwarded_for = request.headers.getlist("X-Forwarded-For")
        if x_forwarded_for:
            ip = x_forwarded_for[0]
        else:
            ip = request.remote_addr
        ctx['search'].result_container.answers.clear()
        ctx['search'].result_container.answers.add(ip)
    elif p.match(ctx['search'].query):
        ua = request.user_agent
        ctx['search'].result_container.answers.clear()
        ctx['search'].result_container.answers.add(ua)
    return True
