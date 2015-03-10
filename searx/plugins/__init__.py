from searx.plugins import self_ip
from searx import logger
from sys import exit

logger = logger.getChild('plugins')

required_attrs = ('name',
                  'description',
                  'default_on')


class Plugin():
    default_on = False
    name = 'Default plugin'


class PluginStore():

    def __init__(self):
        self.plugins = []

    def __iter__(self):
        for plugin in plugins:
            yield plugin

    def register(self, *plugins):
        for plugin in plugins:
            for plugin_attr in required_attrs:
                if not hasattr(plugin, plugin_attr):
                    logger.critical('missing attribute "{0}", cannot load plugin: {1}'.format(plugin_attr, plugin))
                    exit(3)
            self.plugins.append(plugin)

    def call(self, plugin_type, request, *args, **kwargs):
        ret = True
        for plugin in self.plugins:
            if hasattr(plugin, plugin_type):
                ret = getattr(plugin, plugin_type)(request, *args, **kwargs)
                if not ret:
                    break

        return ret


plugins = PluginStore()
plugins.register(self_ip)
