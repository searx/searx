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
from sys import exit
from searx import logger

logger = logger.getChild('plugins')

from searx.plugins import (https_rewrite,
                           open_results_on_new_tab,
                           self_info,
                           search_on_category_select,
                           tracker_url_remover)

required_attrs = (('name', str),
                  ('description', str),
                  ('default_on', bool))

optional_attrs = (('js_dependencies', tuple),
                  ('css_dependencies', tuple))


class Plugin():
    default_on = False
    name = 'Default plugin'
    description = 'Default plugin description'


class PluginStore():

    def __init__(self):
        self.plugins = []

    def __iter__(self):
        for plugin in self.plugins:
            yield plugin

    def register(self, *plugins):
        for plugin in plugins:
            for plugin_attr, plugin_attr_type in required_attrs:
                if not hasattr(plugin, plugin_attr) or not isinstance(getattr(plugin, plugin_attr), plugin_attr_type):
                    logger.critical('missing attribute "{0}", cannot load plugin: {1}'.format(plugin_attr, plugin))
                    exit(3)
            for plugin_attr, plugin_attr_type in optional_attrs:
                if not hasattr(plugin, plugin_attr) or not isinstance(getattr(plugin, plugin_attr), plugin_attr_type):
                    setattr(plugin, plugin_attr, plugin_attr_type())
            plugin.id = plugin.name.replace(' ', '_')
            self.plugins.append(plugin)

    def call(self, plugin_type, request, *args, **kwargs):
        ret = True
        for plugin in request.user_plugins:
            if hasattr(plugin, plugin_type):
                ret = getattr(plugin, plugin_type)(request, *args, **kwargs)
                if not ret:
                    break

        return ret


plugins = PluginStore()
plugins.register(https_rewrite)
plugins.register(open_results_on_new_tab)
plugins.register(self_info)
plugins.register(search_on_category_select)
plugins.register(tracker_url_remover)
