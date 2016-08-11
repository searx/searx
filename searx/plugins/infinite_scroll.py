from flask_babel import gettext

name = gettext('Infinite scroll')
description = gettext('Automatically load next page when scrolling to bottom of current page')
default_on = False

js_dependencies = ('plugins/js/infinite_scroll.js',)
css_dependencies = ('plugins/css/infinite_scroll.css',)
