# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Version numbers and other package META data"""

VERSION_MAJOR = 0
VERSION_MINOR = 16
VERSION_BUILD = 0

VERSION_STRING = "{0}.{1}.{2}".format(
    VERSION_MAJOR,
    VERSION_MINOR,
    VERSION_BUILD
)

# built-in plugins
BUILTIN_PLUGINS = [
    'oa_doi_rewrite',
    'https_rewrite',
    'infinite_scroll',
    'open_results_on_new_tab',
    'self_info',
    'search_on_category_select',
    'tracker_url_remover',
    'vim_hotkeys'
]

PLUGIN_ENTRY_POINTS = [
    '%s = searx.plugins.%s' % (name, name)
    for name in BUILTIN_PLUGINS
]
