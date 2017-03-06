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
import re
from flask_babel import gettext
from requests import get
from searx import settings


name = "Self Information"
description = gettext('Displays your IP if the query is "ip" and your user agent if the query contains "user agent".')
default_on = True


# Self User Agent regex
p = re.compile('.*user[ -]agent.*', re.IGNORECASE)


# Returns a string with all the information retrieved from ip-api.com's API
def get_ip(request):
    x_forwarded_for = request.headers.getlist("X-Forwarded-For")

    if x_forwarded_for:
        ip = x_forwarded_for[0]
    else:
        ip = request.remote_addr

    if ip == '127.0.0.1':
        ip = ''

    # Find the outgoing proxies settings from the user configuration.
    outgoing_proxies = settings['outgoing'].get('proxies', None)

    # Initiate a GET request and set the outgoing proxies, if any were set in
    # settings.yml.
    ip_info = get('http://ipinfo.io/' + (ip + '/' if ip else '') + 'json/', proxies=outgoing_proxies).json()

    # Return the formatted string.
    return "Your IP is %s from %s, %s, provided by %s" % (
        ip_info['ip'],
        ip_info['city'],
        ip_info['country'],
        ip_info['org'])


# attach callback to the post search hook
#  request: flask request object
#  ctx: the whole local context of the pre search hook
def post_search(request, search):
    if search.search_query.pageno > 1:
        return True
    if search.search_query.query == 'ip':
        search.result_container.answers.clear()
        search.result_container.answers.add(get_ip(request))
    elif p.match(search.search_query.query):
        ua = request.user_agent
        search.result_container.answers.clear()
        search.result_container.answers.add(ua)
    return True
