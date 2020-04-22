# SPDX-License-Identifier: AGPL-3.0-or-later
"""A searx plugin is a namespace that consists of :py:obj:`required
<required_attrs>` and :py:obj:`optional <optional_attrs>` attributes (names).  A
*prototype* of such a namespace is implemented in class :py:class:`Plugin` (see
:ref:`dev plugin`):

- :py:obj:`ENTRY_POINT_NAME` / :py:func:`PluginStore.load_entry_points`
- :py:func:`get_plugins` / :py:class:`PluginStore`
- :py:class:`Plugin` / :py:class:`PluginInvalidError`
- :py:obj:`required_attrs` and :py:class:`optional_attrs`

"""

__all__ = [
    'get_plugins', 'ENTRY_POINT_NAME', 'Plugin', 'PluginInvalidError', 'PluginStore',
    'required_attrs', 'optional_attrs',
]

import sys
import inspect
import pkg_resources

from searx import logger
from searx.resources import (
    SEARX_DIR,
    File,
)
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

ENTRY_POINT_NAME = 'searx.plugins'
"""Name of the entry point to get *builtin* and *external* plugins"""

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
    ('css_dependencies', tuple),
    ('pre_search', callable ),
    ('post_search', callable ),
    ('on_result', callable ),
)
"""Optional attributes, see :py:class:`.Plugin`.

- :py:class:`Plugin.js_dependencies` (tuple)
- :py:class:`Plugin.css_dependencies` (tuple)
- :py:class:`Plugin.pre_search` (callable)
- :py:class:`Plugin.post_search` (callable)
- :py:class:`Plugin.on_result` (callable)
"""

# Global plugin store
_store = None
def get_plugins():
    """Returns *global* plugin-store.  If not not already inited, the *global* store
    is loaded with *builtin* plugins.  For initialization, application should call
    this function once when preparing the context for the main loop.

    :rtype: PluginStore
    :return: global plugin store

    """
    global _store  # pylint: disable=global-statement

    if _store is None:
        _store = PluginStore()
        _store.load_entry_points()
    return _store

class PluginInvalidError(Exception):
    """Raised when a plugin in is invalid"""

class Plugin:  # pylint: disable=R0903
    """Prototype of plugin's *namespace*.
    """

    name = None
    """Name of the plugin (:py:obj:`required_attrs`)."""

    default_on = None
    """Plugin disabled or enabled by default (:py:obj:`required_attrs`)."""

    description = None
    """One-liner description of the plugin (:py:obj:`required_attrs`)"""

    js_dependencies = None
    """:py:obj:`Optional <optional_attrs>` list of static JS files.  URL pathes of
    JavaScript files, the plugin loads on the client site::

        ('plugins/js/<plugin-name>/<module>.js', ...)

    """

    css_dependencies = None
    """:py:obj:`Optional <optional_attrs>` list of static CSS files.  URL pathes of
    CSS files, the plugin loads on the client site::

        ('plugins/css/<plugin-name>/<module>.css', ...)

    """

    @classmethod
    def pre_search(cls, request, ctx):
        """A handle that runs **before** the search request.

        :type request:   flask.request
        :param request:  :py:obj:`flask request object <flask.request>`

        :type ctx:   searx.search.SearchWithPlugins
        :param ctx:  the whole local context of the pre search hook
        """

    @classmethod
    def post_search(cls, request, ctx):
        """A handle that runs **after** the search request

        :type request:   flask.request
        :param request:  :py:obj:`flask request object <flask.request>`

        :type ctx:   searx.search.SearchWithPlugins
        :param ctx:  the whole local context of the post search hook
        """

    @classmethod
    def on_result(cls, request, ctx, result):
        """A handle that runs when a new result is added to the result list.

        :type request:   flask.request
        :param request:  :py:obj:`flask request object <flask.request>`

        :type ctx:   searx.search.SearchWithPlugins
        :param ctx:  the whole local context of the post search hook

        :type result:   searx.results.ResultContainer
        :param result:  :py:obj:`result container <searx.results.ResultContainer>`

        """

class PluginStore:
    """Plugin management

    """

    def __init__(self):
        self.plugins = dict()

    def reset(self):
        """Drop plugins from store, re-init store."""
        self.__init__()

    def __iter__(self):
        """Iterates over registered plugins"""
        for plugin in self.plugins.values():
            yield plugin

    def __len__(self):
        return len(self.plugins)

    def getattr(self, name):
        """Generator that iterats over all plugins yielding attribute ``name``.

        :type name: str
        :param name: Name in plugin's namespace.
        """
        for plugin in self.plugins.values():
            yield  getattr(plugin, name)

    def call(self, plugin_list, name, *args, **kwargs):
        # pylint: disable=anomalous-backslash-in-string
        """Call function *name* on each plugin and return a list of the return values.

        :type plugin_list:  [ searx.plugins.Plugin, ]
        :param plugin_list: list of (ordered) :py:class:`PlugIn`

        :type name: str
        :param name: In plugin's namespace; name of the function to call.  If
                     one plugin does not have this name, non function is called
                     and a :py:obj:`AttributeError` is raised.

        :type \*args: object
        :param \*args: Positional arguments passed trough the function.

        :type \*kwargs: object
        :param \*kwargs: Keyword arguments passed trough the function.

        :rtype: list
        :return: List of the return values from each call.

        :raises AttributeError: If one plugin does not have this name.

        """
        ret_val = []
        if plugin_list is None:
            plugin_list = self

        f_list = [ getattr(p, name) for p in plugin_list ]
        for func in f_list:
            ret_val.append(func(*args, **kwargs))
        return ret_val

    def load_entry_points(self):
        """Load :py:class:`PluginStore` with plugins from python ``entry_points``
        named ``searx.plugins``.

        """
        for plugin_ep in pkg_resources.iter_entry_points(ENTRY_POINT_NAME):
            self.register(plugin_ep.load(), plugin_ep.name)

    def register(self, plugin, plugin_id):
        """Register a plugin.  Before the plugin is registered, the
        :py:obj`required_attrs` and :py:obj:`optional_attrs` attributes (names)
        from plugin's namespace are validated and plugin's namespace is
        :py:func:`normalized <PluginStore.normalize_plugin>`.

        :type plugin:  PlugIn, module
        :param plugin: plugin's namespace

        :type plugin_id:  str
        :param plugin_id: Identifier of the plugin, normaly the name of the
                          entry point (also used in path names)

        """
        try:
            if plugin_id in self.plugins.keys():
                raise PluginInvalidError(
                    "Plugin plugin_id %s already exists: %s // plugin: %s"
                    % (plugin_id, self.plugins[plugin_id], plugin))
            self.validate_plugin(plugin)

        except PluginInvalidError as exc:
            logger.critical(str(exc))
            sys.exit(3)

        self.normalize_plugin(plugin, plugin_id)
        self.plugins[plugin_id] = plugin

    @classmethod
    def normalize_plugin(cls, plugin, plugin_id):
        """Set ``plugin_id`` and missing (optional) attributes in plugin's namespace.

        :type plugin:  PlugIn, module
        :param plugin: plugin's namespace

        :type plugin_id:  str
        :param plugin_id: Identifier of the plugin, normaly the name of the
                          entry point (also used in path names)
        """

        plugin.id = plugin_id
        for plugin_attr, plugin_attr_type in optional_attrs:
            if not hasattr(plugin, plugin_attr):
                # pylint: disable=comparison-with-callable
                if plugin_attr_type == callable:
                    # set nope function that returns true
                    setattr(plugin, plugin_attr, lambda *args, **kwargs: True)
                else:
                    # set dummy object by instatiating data type
                    setattr(plugin, plugin_attr, plugin_attr_type())

    @classmethod
    def validate_plugin(cls, plugin):
        """The :py:obj`required_attrs` and :py:obj:`optional_attrs` attributes (names)
        from plugin's namespace are validated.  If plugin is not valid, a
        :py:class:`ValidationError` exception is raised.

        :type plugin:   module, Plugin
        :param plugin:  plugin's namespace

        """

        def assert_type(plugin_attr, plugin_attr_type):
            # pylint: disable=comparison-with-callable
            if plugin_attr_type == callable:
                if not callable(getattr(plugin, plugin_attr)):
                    raise PluginInvalidError(
                        'attribute "{0}" is not callable, plugin: {1}'.format(
                            plugin_attr, plugin))
            elif not isinstance(getattr(plugin, plugin_attr), plugin_attr_type):
                raise PluginInvalidError(
                    'attribute "{0}" is not instance of type {1}, plugin: {2}'.format(
                        plugin_attr, plugin_attr_type, plugin))

        # validate required and types
        for plugin_attr, plugin_attr_type in required_attrs:
            if not hasattr(plugin, plugin_attr):
                raise PluginInvalidError(
                    'missing attribute "{0}", cannot load plugin: {1}'.format(
                        plugin_attr, plugin))
            assert_type(plugin_attr, plugin_attr_type)

        # validate optional types
        for plugin_attr, plugin_attr_type in optional_attrs:
            if hasattr(plugin, plugin_attr):
                assert_type(plugin_attr, plugin_attr_type)

        # check origin static files
        for fname, static_url in cls.iter_static_files(plugin):
            if not fname.EXISTS:
                raise PluginInvalidError(
                    'missing file "{0}", plugin: {1}'.format(
                        fname, plugin))

    @classmethod
    def iter_static_files(cls, plugin):
        """Iterates all static files.  For each static file a tuple is returned containing:

        1. ``fname``: (:py:class:`searx.resources.File`): location of the file in
           the repository.

        2. ``static_url``: (:py:class:`searx.resources.File`): relative URL of the
           static file.  The base path of this relative URL is a URL that points
           to :py:obj:`searx.resources.StaticFiles.path`.

        """
        for dep_attr in ('js_dependencies', 'css_dependencies'):
            for static_url in getattr(plugin, dep_attr, []):
                static_url = File(static_url)

                # the static files of builtin plugins are located at
                # /usr/local/searx/searx-src/searx/static/plugins/
                fname = SEARX_DIR / 'static' / static_url

                yield (fname, static_url)
