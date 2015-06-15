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

regexes = {re.compile(r'utm_[^&]+&?'),
           re.compile(r'(wkey|wemail)[^&]+&?'),
           re.compile(r'&$')}

name = gettext('Tracker URL remover')
description = gettext('Remove trackers arguments from the returned URL')
default_on = True


def on_result(request, ctx):
    splited_url = ctx['result']['url'].split('?')

    if len(splited_url) is not 2:
        return True

    for reg in regexes:
        splited_url[1] = reg.sub('', splited_url[1])

    if splited_url[1] == "":
        ctx['result']['url'] = splited_url[0]
    else:
        ctx['result']['url'] = splited_url[0] + '?' + splited_url[1]

    return True
