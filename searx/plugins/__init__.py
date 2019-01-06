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
from sys import exit, version_info
from os.path import realpath, dirname
from searx import logger, settings
from searx.utils import load_module


if version_info[0] == 3:
    unicode = str

logger = logger.getChild('plugins')

required_attrs = (('name', (str, unicode)),
                  ('description', (str, unicode)),
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

    def call(self, ordered_plugin_list, plugin_type, request, *args, **kwargs):
        ret = True
        for plugin in ordered_plugin_list:
            if hasattr(plugin, plugin_type):
                ret = getattr(plugin, plugin_type)(request, *args, **kwargs)
                if not ret:
                    break

        return ret


plugins = PluginStore()
plugin_dir = dirname(realpath(__file__))
if 'plugins' in settings and isinstance(settings['plugins'], list):
    for plugin_module in settings['plugins']:
        if isinstance(plugin_module, str):
            plugin_name = plugin_module
        elif isinstance(plugin_module, dict):
            plugin_name = plugin_module['name']
            if plugin_module.get('disabled', False):
                logger.debug('Plugin "{}" is disabled'.format(plugin_name))
                continue
        else:
            logger.debug('Weird plugin "{}"'.format(str(plugin_module)))
            continue
        try:
            plg = load_module(plugin_name + '.py', plugin_dir)
        except ImportError:
            logger.exception('Cannot load plugin "{}"'.format(plugin_name))
            continue
        plugins.register(plg)
