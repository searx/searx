from flask.ext.babel import gettext
name = 'Search on category select'
description = gettext('Perform search immediately if a category selected')
default_on = False

js_dependencies = ('js/search_on_category_select.js',)
