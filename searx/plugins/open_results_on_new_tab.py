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

(C) 2016 by Adam Tauber, <asciimoo@gmail.com>
'''
from flask_babel import gettext
name = gettext('Open result links on new browser tabs')
description = gettext('Results are opened in the same window by default. '
                      'This plugin overwrites the default behaviour to open links on new tabs/windows. '
                      '(JavaScript required)')
default_on = False

js_dependencies = ('plugins/js/open_results_on_new_tab.js',)
