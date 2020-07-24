from flask_babel import gettext

name = gettext('Infinite scroll')
description = gettext('Automatically load next page when scrolling to bottom of current page')
default_on = False
preference_section = 'ui'

js_dependencies = ('resources/infinite_scroll.js',)
css_dependencies = ('resources/infinite_scroll.css',)
