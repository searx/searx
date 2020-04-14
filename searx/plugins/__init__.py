# SPDX-License-Identifier: AGPL-3.0-or-later
"""A searx plugin is a namespace that consists of :py:obj:`required
<required_attrs>` and :py:obj:`optional <optional_attrs>` attributes (names).  A
*prototype* of such a namespace is implemented in class :py:class:`Plugin` (see
:ref:`dev plugin`).

"""

__all__ = [
    'plugins', 'Plugin', 'PluginStore',
    'required_attrs', 'optional_attrs',
    'build_plugin_store'
]

import sys
from searx import logger

from searx.plugins import (
    oa_doi_rewrite,
    https_rewrite,
    infinite_scroll,
    open_results_on_new_tab,
    self_info,
    search_on_category_select,
    tracker_url_remover,
    vim_hotkeys
)

logger = logger.getChild('plugins')

if sys.version_info[0] == 3:
    # pylint: disable=C0103
    unicode = str

required_attrs = (
    ('name', (str, unicode)),
    ('description', (str, unicode)),
    ('default_on', bool)
)
"""Required attributes, see :py:class:`.Plugin`.

- :py:class:`Plugin.name` (unicode)
- :py:class:`Plugin.description` (unicode)
- :py:class:`Plugin.default_on` (bool)
"""

optional_attrs = (
    ('js_dependencies', tuple),
    ('css_dependencies', tuple)
)
"""Optional attributes, see :py:class:`.Plugin`.

- :py:class:`Plugin.js_dependencies` (tuple)
- :py:class:`Plugin.css_dependencies` (tuple)
"""

class Plugin():  # pylint: disable=R0903
    """Prototype of plugin's *namespace*.
    """

    name = 'Default plugin'
    """Name of the plugin (:py:obj:`required_attrs`)."""

    default_on = False
    """Plugin disabled or enabled by default (:py:obj:`required_attrs`)."""

    description = 'Default plugin description'
    """One-liner description of the plugin (:py:obj:`required_attrs`)"""

    js_dependencies = tuple()
    """:py:obj:`Optional <optional_attrs>` list of static JS files.  URL pathes of
    JavaScript files, the plugin loads on the client site::

        ('plugins/js/<plugin-name>/<module>.js', ...)

    """

    css_dependencies = tuple()
    """:py:obj:`Optional <optional_attrs>` list of static CSS files.  URL pathes of
    CSS files, the plugin loads on the client site::

        ('plugins/css/<plugin-name>/<module>.css', ...)

    """

    def pre_search(self, request, ctx):
        """A handle that runs **before** the search request.

        :type request:   flask.request
        :param request:  :py:obj:`flask request object <flask.request>`

        :type ctx:   searx.search.SearchWithPlugins
        :param ctx:  the whole local context of the pre search hook
        """

    def on_result(self, request, ctx, result):
        """A handle that runs when a new result is added to the result list.

        :type request:   flask.request
        :param request:  :py:obj:`flask request object <flask.request>`

        :type ctx:   searx.search.SearchWithPlugins
        :param ctx:  the whole local context of the post search hook

        :type result:   searx.results.ResultContainer
        :param result:  :py:obj:`result container <searx.results.ResultContainer>`

        """

    def post_search(self, request, ctx):
        """A handle that runs **after** the search request

        :type request:   flask.request
        :param request:  :py:obj:`flask request object <flask.request>`

        :type ctx:   searx.search.SearchWithPlugins
        :param ctx:  the whole local context of the post search hook
        """

class PluginStore():
    """Plugin management

    """

    def __init__(self):
        self.plugins = []

    def __iter__(self):
        for plugin in self.plugins:
            yield plugin

    def register(self, *namespaces):
        """register plugins *(aka namespaces)*"""
        for plugin in namespaces:
            for plugin_attr, plugin_attr_type in required_attrs:
                if ( not hasattr(plugin, plugin_attr)
                     or not isinstance(
                         getattr(plugin, plugin_attr), plugin_attr_type )):
                    logger.critical(
                        'missing attribute "{0}", cannot load plugin: {1}'.format(
                            plugin_attr, plugin))
                    sys.exit(3)
            for plugin_attr, plugin_attr_type in optional_attrs:
                if ( not hasattr(plugin, plugin_attr)
                     or not isinstance(
                         getattr(plugin, plugin_attr), plugin_attr_type )):
                    setattr(plugin, plugin_attr, plugin_attr_type())
            plugin.id = plugin.name.replace(' ', '_')
            self.plugins.append(plugin)

    def call(  # pylint: disable=missing-function-docstring, no-self-use
            self, ordered_plugin_list, plugin_type, request, *args, **kwargs):
        ret = True
        for plugin in ordered_plugin_list:
            if hasattr(plugin, plugin_type):
                ret = getattr(plugin, plugin_type)(request, *args, **kwargs)
                if not ret:
                    break

        return ret

def build_plugin_store():
    """Build plugin store from :py:class:`PluginStore` and load *builtins*.
    """
    s = PluginStore()
    s.register(oa_doi_rewrite)
    s.register(https_rewrite)
    s.register(infinite_scroll)
    s.register(open_results_on_new_tab)
    s.register(self_info)
    s.register(search_on_category_select)
    s.register(tracker_url_remover)
    s.register(vim_hotkeys)
    return s

plugins = build_plugin_store()
"""Global plugin store, created by function :py:func:`build_plugin_store`"""
