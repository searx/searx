from searx.plugins import self_ip
from searx import logger
from sys import exit

logger = logger.getChild('plugins')

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
plugins.register(self_ip)
