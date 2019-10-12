from flask_babel import gettext

name = gettext('Progressive Web Application')
description = gettext('Allow searx to be installed on a phone almost as if it was a Native App.')
default_on = True
preference_section = 'ui'

js_dependencies = ('plugins/js/pwa.js',)
css_dependencies = ('plugins/css/pwa.css',)
