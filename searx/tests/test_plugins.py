# -*- coding: utf-8 -*-

from searx.testing import SearxTestCase
from searx import plugins
from mock import Mock


class PluginStoreTest(SearxTestCase):

    def test_PluginStore_init(self):
        store = plugins.PluginStore()
        self.assertTrue(isinstance(store.plugins, list) and len(store.plugins) == 0)

    def test_PluginStore_register(self):
        store = plugins.PluginStore()
        testplugin = plugins.Plugin()
        store.register(testplugin)

        self.assertTrue(len(store.plugins) == 1)

    def test_PluginStore_call(self):
        store = plugins.PluginStore()
        testplugin = plugins.Plugin()
        store.register(testplugin)
        setattr(testplugin, 'asdf', Mock())
        request = Mock(user_plugins=[])
        store.call('asdf', request, Mock())

        self.assertFalse(testplugin.asdf.called)

        request.user_plugins.append(testplugin)
        store.call('asdf', request, Mock())

        self.assertTrue(testplugin.asdf.called)


class SelfIPTest(SearxTestCase):

    def test_PluginStore_init(self):
        store = plugins.PluginStore()
        store.register(plugins.self_ip)

        self.assertTrue(len(store.plugins) == 1)

        request = Mock(user_plugins=store.plugins,
                       remote_addr='127.0.0.1')
        request.headers.getlist.return_value = []
        ctx = {'search': Mock(answers=set(),
                              query='ip')}
        store.call('post_search', request, ctx)
        self.assertTrue('127.0.0.1' in ctx['search'].answers)
