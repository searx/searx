# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=missing-function-docstring, missing-class-docstring

from collections.abc import Iterable
from mock import Mock

from searx import plugins
from searx.testing import SearxTestCase

def get_search_mock(query, **kwargs):
    return Mock(search_query=Mock(query=query, **kwargs),
                result_container=Mock(answers=set()))

class UnitTestPlugin(plugins.PluginStore):
    name = "test plugin"
    description = "PLugin of the unit test"
    default_on = False

class PluginStoreTest(SearxTestCase):

    def test_PluginStore_init(self):
        store = plugins.PluginStore()
        self.assertTrue(isinstance(store, Iterable) and len(store) == 0)

    def test_PluginStore_register(self):
        store = plugins.PluginStore()
        testplugin = UnitTestPlugin()
        store.register(testplugin, 'unittestplugin')

        self.assertTrue(len(store.plugins) == 1)

    def test_PluginStore_call(self):
        store = plugins.PluginStore()
        testplugin = UnitTestPlugin()
        store.register(testplugin, 'unittestplugin')
        # pylint: disable=no-member
        setattr(testplugin, 'asdf', Mock())
        request = Mock()
        store.call([], 'asdf', request, Mock())

        self.assertFalse(testplugin.asdf.called)

        store.call([testplugin], 'asdf', request, Mock())
        self.assertTrue(testplugin.asdf.called)


class SelfIPTest(SearxTestCase):

    @classmethod
    def _get_store(cls):
        store = plugins.PluginStore()
        store.register(plugins.self_info, 'self_info')
        return store

    def test_PluginStore_init(self):
        store = self._get_store()
        self.assertTrue(len(store.plugins) == 1)

    def test_IP(self):
        # IP test
        store = self._get_store()
        request = Mock(remote_addr='127.0.0.1')
        request.headers.getlist.return_value = []
        search = get_search_mock(query=b'ip', pageno=1)
        store.call(list(store), 'post_search', request, search)
        self.assertTrue('127.0.0.1' in search.result_container.answers)

        search = get_search_mock(query=b'ip', pageno=2)
        store.call(list(store), 'post_search', request, search)
        self.assertFalse('127.0.0.1' in search.result_container.answers)

    def test_user_agent(self):
        # User agent test
        store = self._get_store()
        request = Mock(user_agent='Mock')
        request.headers.getlist.return_value = []

        search = get_search_mock(query=b'user-agent', pageno=1)
        store.call(list(store), 'post_search', request, search)
        self.assertTrue('Mock' in search.result_container.answers)

        search = get_search_mock(query=b'user-agent', pageno=2)
        store.call(list(store), 'post_search', request, search)
        self.assertFalse('Mock' in search.result_container.answers)

        search = get_search_mock(query=b'user-agent', pageno=1)
        store.call(list(store), 'post_search', request, search)
        self.assertTrue('Mock' in search.result_container.answers)

        search = get_search_mock(query=b'user-agent', pageno=2)
        store.call(list(store), 'post_search', request, search)
        self.assertFalse('Mock' in search.result_container.answers)

        search = get_search_mock(query=b'What is my User-Agent?', pageno=1)
        store.call(list(store), 'post_search', request, search)
        self.assertTrue('Mock' in search.result_container.answers)

        search = get_search_mock(query=b'What is my User-Agent?', pageno=2)
        store.call(list(store), 'post_search', request, search)
        self.assertFalse('Mock' in search.result_container.answers)
