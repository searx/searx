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

from importlib import import_module
from os.path import abspath, basename, dirname, exists, join
from shutil import copyfile
from sys import exit, version_info
from traceback import print_exc

from searx import logger, settings, static_path

if version_info[0] == 3:
    unicode = str

logger = logger.getChild('plugins')

from searx.plugins import (oa_doi_rewrite,
                           https_rewrite,
                           infinite_scroll,
                           open_results_on_new_tab,
                           self_info,
                           search_on_category_select,
                           tracker_url_remover,
                           vim_hotkeys)

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

    def register(self, *plugins, external=False):
        if external:
            plugins = load_external_plugins(plugins)
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


def load_external_plugins(plugin_names):
    plugins = []
    for name in plugin_names:
        logger.debug('loading plugin: {0}'.format(name))
        try:
            pkg = import_module(name)
        except Exception as e:
            logger.critical('failed to load plugin module {0}: {1}'.format(name, e))
            exit(3)

        pkg.__base_path = dirname(abspath(pkg.__file__))

        fix_package_resources(pkg, name)

        plugins.append(pkg)
        logger.debug('plugin "{0}" loaded'.format(name))
    return plugins


def check_resource(base_path, resource_path, name, dir_prefix):
        dep_path = join(base_path, resource_path)
        file_name = basename(dep_path)
        resource_name = '{0}_{1}'.format('_'.join(name.split()), file_name)
        resource_path = join(static_path, 'plugins', dir_prefix, resource_name)
        if not exists(resource_path):
            try:
                copyfile(dep_path, resource_path)
            except:
                logger.critical('failed to copy plugin resource {0} for plugin {1}'.format(resource_name, name))
                exit(3)

        # returning with the web path of the resource
        return join('plugins', dir_prefix, resource_name)


def fix_package_resources(pkg, name):
    if hasattr(pkg, 'js_dependencies'):
        pkg.js_dependencies = tuple([
            check_resource(pkg.__base_path, x, name, 'js')
            for x in pkg.js_dependencies
        ])
    if hasattr(pkg, 'css_dependencies'):
        pkg.css_dependencies = tuple([
            check_resource(pkg.__base_path, x, name, 'css')
            for x in pkg.css_dependencies
        ])


plugins = PluginStore()
plugins.register(oa_doi_rewrite)
plugins.register(https_rewrite)
plugins.register(infinite_scroll)
plugins.register(open_results_on_new_tab)
plugins.register(self_info)
plugins.register(search_on_category_select)
plugins.register(tracker_url_remover)
plugins.register(vim_hotkeys)
# load external plugins
if 'plugins' in settings:
    plugins.register(*settings['plugins'], external=True)
