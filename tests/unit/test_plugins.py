# -*- coding: utf-8 -*-

from searx.testing import SearxTestCase
from searx import plugins
from searx.plugins.spellchecker import levenshtein, spell_corrections, corrections_from_suggestions
from mock import Mock


def get_search_mock(query, **kwargs):
    return {'search': Mock(query=query,
                           result_container=Mock(answers=set()),
                           **kwargs)}


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
        store.register(plugins.self_info)

        self.assertTrue(len(store.plugins) == 1)

        # IP test
        request = Mock(user_plugins=store.plugins,
                       remote_addr='127.0.0.1')
        request.headers.getlist.return_value = []
        ctx = get_search_mock(query='ip')
        store.call('post_search', request, ctx)
        self.assertTrue('127.0.0.1' in ctx['search'].result_container.answers)

        # User agent test
        request = Mock(user_plugins=store.plugins,
                       user_agent='Mock')
        request.headers.getlist.return_value = []

        ctx = get_search_mock(query='user-agent')
        store.call('post_search', request, ctx)
        self.assertTrue('Mock' in ctx['search'].result_container.answers)

        ctx = get_search_mock(query='user-agent')
        store.call('post_search', request, ctx)
        self.assertTrue('Mock' in ctx['search'].result_container.answers)

        ctx = get_search_mock(query='What is my User-Agent?')
        store.call('post_search', request, ctx)
        self.assertTrue('Mock' in ctx['search'].result_container.answers)


class SpellCheckerTest(SearxTestCase):

    def test_SpellChecker_init(self):
        store = plugins.PluginStore()
        store.register(plugins.spellchecker)

        self.assertTrue(len(store.plugins) == 1)

    def test_levenshtein(self):
        self.assertEqual(levenshtein("", ""), 0)
        self.assertEqual(levenshtein("hello", "hello"), 0)
        self.assertEqual(levenshtein("", "hello"), 5)
        self.assertEqual(levenshtein("hello", ""), 5)
        self.assertEqual(levenshtein("kitten", "sitting"), 3)
        self.assertEqual(levenshtein(u"m\u00FChle", "muehle"), 2)
        self.assertEqual(levenshtein(u"Linux", "linux"), 1)

    def test_spell_corrections(self):
        directory = ("annotate", "annotated", "annotates", "annotating",
                     "annotation", "annotations", "announce", "announced",
                     "announcement", "announcements", "announcer", "announcers",
                     "announces", "announcing", "annoy", "annoyance")

        corrections = spell_corrections("annotatd", directory, 3)
        self.assertEqual(len(corrections), 5)
        self.assertTrue('annotate' in corrections)
        self.assertTrue('annotated' in corrections)
        self.assertTrue('annotates' in corrections)
        self.assertTrue('annotating' in corrections)
        self.assertTrue('annotation' in corrections)

        corrections = spell_corrections("announcement", directory, 3)
        self.assertEqual(len(corrections), 2)
        self.assertTrue('announcement' in corrections)
        self.assertTrue('announcements' in corrections)

        corrections = spell_corrections("hello", directory, 3)
        self.assertEqual(len(corrections), 0)

    def test_corrections_from_suggestions(self):
        suggestions = ("a privacy respecting, hackable metasearch engine",
                       "python based search engine", "open source software")

        corrections = corrections_from_suggestions("opn sorce serch engine", suggestions)
        self.assertEqual(len(corrections), 1)
        self.assertTrue("open source search engine" in corrections)

        corrections = corrections_from_suggestions("open source search engine", suggestions)
        self.assertEqual(len(corrections), 0)

        corrections = corrections_from_suggestions("openstreetma", suggestions)
        self.assertEqual(len(corrections), 0)
