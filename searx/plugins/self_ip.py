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
name = "Self IP"
description = gettext('Display your source IP address if the query expression is "ip"')
default_on = True


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
        ctx['search'].answers.clear()
        ctx['search'].answers.add(ip)
    return True
