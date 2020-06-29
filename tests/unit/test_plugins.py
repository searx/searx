# -*- coding: utf-8 -*-
from searx.testing import SearxTestCase
from searx import plugins
from mock import Mock

from searx.webapp import app


def get_search_mock(query, **kwargs):
    return Mock(search_query=Mock(query=query, **kwargs),
                result_container=Mock(answers=dict()))


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
        request = Mock()
        store.call([], 'asdf', request, Mock())

        self.assertFalse(testplugin.asdf.called)

        store.call([testplugin], 'asdf', request, Mock())
        self.assertTrue(testplugin.asdf.called)


class SelfIPTest(SearxTestCase):

    def test_PluginStore_init(self):
        store = plugins.PluginStore()
        store.register(plugins.self_info)

        self.assertTrue(len(store.plugins) == 1)

        # IP test
        request = Mock(remote_addr='127.0.0.1')
        request.headers.getlist.return_value = []
        search = get_search_mock(query=b'ip', pageno=1)
        store.call(store.plugins, 'post_search', request, search)
        self.assertTrue('127.0.0.1' in search.result_container.answers["ip"]["answer"])

        search = get_search_mock(query=b'ip', pageno=2)
        store.call(store.plugins, 'post_search', request, search)
        self.assertFalse('ip' in search.result_container.answers)

        # User agent test
        request = Mock(user_agent='Mock')
        request.headers.getlist.return_value = []

        search = get_search_mock(query=b'user-agent', pageno=1)
        store.call(store.plugins, 'post_search', request, search)
        self.assertTrue('Mock' in search.result_container.answers["user-agent"]["answer"])

        search = get_search_mock(query=b'user-agent', pageno=2)
        store.call(store.plugins, 'post_search', request, search)
        self.assertFalse('user-agent' in search.result_container.answers)

        search = get_search_mock(query=b'user-agent', pageno=1)
        store.call(store.plugins, 'post_search', request, search)
        self.assertTrue('Mock' in search.result_container.answers["user-agent"]["answer"])

        search = get_search_mock(query=b'user-agent', pageno=2)
        store.call(store.plugins, 'post_search', request, search)
        self.assertFalse('user-agent' in search.result_container.answers)

        search = get_search_mock(query=b'What is my User-Agent?', pageno=1)
        store.call(store.plugins, 'post_search', request, search)
        self.assertTrue('Mock' in search.result_container.answers["user-agent"]["answer"])

        search = get_search_mock(query=b'What is my User-Agent?', pageno=2)
        store.call(store.plugins, 'post_search', request, search)
        self.assertFalse('user-agent' in search.result_container.answers)


class SelfBangTest(SearxTestCase):

    def test_PluginStore_init(self):
        store = plugins.PluginStore()
        store.register(plugins.bangs)
        request = Mock(remote_addr='127.0.0.1')

        self.assertTrue(len(store.plugins) == 1)

        # Valid Bang redirect test
        search_valid = get_search_mock(query='!!yt never gonna give you up')

        store.call(store.plugins, 'pre_search', search_valid, request)

        # For checking what the redirect URL was.
        self.assertTrue(search_valid.result_container.redirect_url ==
                        "https://www.youtube.com/results?search_query=never%20gonna%20give%20you%20up%20")

        # Invalid Bang redirect test
        invalid_search = get_search_mock(query='youtube never gonna give you up')
        store.call(store.plugins, 'pre_search', invalid_search, request)

        self.assertFalse(invalid_search.result_container.redirect_url ==
                         "https://www.youtube.com/results?search_query=never%20gonna%20give%20you%20up%20")
