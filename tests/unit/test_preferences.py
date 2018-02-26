from searx.preferences import (EnumStringSetting, MapSetting,
                               MissingArgumentException, SearchLanguageSetting,
                               MultipleChoiceSetting, PluginsSetting,
                               ValidationException)
from searx.preferences import Preferences
from searx.testing import SearxTestCase
from searx.engines import engines
from mock import patch, Mock
from parameterized import parameterized
from searx import settings
from searx.languages import language_codes as languages


def get_multiple_choice_setting_mock(default_value, **kwargs):
    return Mock(value=default_value, **kwargs)


def get_search_language_setting_mock(default_value, **kwargs):
    return Mock(value=default_value, choices="en-US")


def get_enum_string_setting_mock(default_value, **kwargs):
    return Mock(value=default_value, **kwargs)


def get_map_setting_mock(default_value, **kwargs):
    return Mock(value=default_value, **kwargs)


def get_plugin_setting_mock(default_value, **kwargs):
    return Mock(value=default_value, **kwargs)


def get_engines_setting_mock(default_value, **kwargs):
    return Mock(value=default_value, **kwargs)


class PluginStub(object):

    def __init__(self, id, default_on):
        self.id = id
        self.default_on = default_on


class PreferencesTest(object):
    def __init__(self, key_value_settings, engines, plugins):
        super(PreferencesTest, self).__init__()

        self.key_value_settings = key_value_settings
        self.engines = get_engines_setting_mock('engines', choices=engines)
        self.plugins = get_plugin_setting_mock('plugins', choices=plugins)
        self.unknown_params = {}


class TestSettings(SearxTestCase):

    @parameterized.expand([
        ([''], [''], [''], ['']),
        (['simple'], ['science'], ['bing', 'google'], [PluginStub(1, False)]),
        (['simple'], ['it, video'], ['json_engine', 'currency_convert',
                                     'deviantart', 'duckduckgo'],
         [PluginStub(1, False)])
    ])
    def test_default_preferences(self, themes, categories, engines, plugins):
        mock_key_value_settings = {
            'categories': get_multiple_choice_setting_mock(['general'],
                                                           choices=categories + ['none']),
            'language': get_search_language_setting_mock(['en-US'],
                                                         choices=[l[0] for l in languages]),
            'locale': get_enum_string_setting_mock('', choices=list(settings['locales'].keys()) +
                                                   ['']),
            'autocomplete': get_enum_string_setting_mock(''),
            'image_proxy': get_map_setting_mock(False, map={'': settings['server']['image_proxy'],
                                                            '0': False,
                                                            '1': True,
                                                            'True': True,
                                                            'False': False}),
            'method': get_enum_string_setting_mock('POST', choices=('GET', 'POST')),
            'safesearch': get_map_setting_mock(0, map={'0': 0, '1': 1, '2': 2}),
            'theme': get_enum_string_setting_mock(['oscar'], choices=themes),
            'results_on_new_tab': get_map_setting_mock(False, map={'0': False,
                                                                   '1': True,
                                                                   'False': False,
                                                                   'True': True}),
            'doi_resolver': get_multiple_choice_setting_mock(['oadoi.org'], choices=list(settings['doi_resolvers']))
        }

        preferences = PreferencesTest(
            mock_key_value_settings, engines, plugins)

        self.assertEquals(
            preferences.key_value_settings['categories'].value, ['general'])
        self.assertEquals(
            preferences.key_value_settings['language'].value, ['en-US'])
        self.assertEquals(preferences.key_value_settings['locale'].value, '')
        self.assertEquals(
            preferences.key_value_settings['autocomplete'].value, '')
        self.assertEquals(
            preferences.key_value_settings['image_proxy'].value, False)
        self.assertEquals(
            preferences.key_value_settings['method'].value, 'POST')
        self.assertEquals(
            preferences.key_value_settings['safesearch'].value, 0)
        self.assertEquals(
            preferences.key_value_settings['theme'].value, ['oscar'])
        self.assertEquals(
            preferences.key_value_settings['results_on_new_tab'].value, False)
        self.assertEquals(
            preferences.key_value_settings['doi_resolver'].value, ['oadoi.org'])

        self.assertEquals(
            preferences.key_value_settings['categories'].choices, categories + ['none'])
        self.assertEquals(
            preferences.key_value_settings['theme'].choices, themes)
        self.assertEquals(preferences.engines.choices, engines)
        self.assertEquals(preferences.plugins.choices, plugins)

    # map settings
    def test_map_setting_invalid_initialization(self):
        with self.assertRaises(MissingArgumentException):
            setting = MapSetting(3, wrong_argument={'0': 0})

    def test_map_setting_invalid_default_value(self):
        with self.assertRaises(ValidationException):
            setting = MapSetting(3, map={'dog': 1, 'bat': 2})

    def test_map_setting_invalid_choice(self):
        setting = MapSetting(2, map={'dog': 1, 'bat': 2})
        with self.assertRaises(ValidationException):
            setting.parse('cat')

    def test_map_setting_valid_default(self):
        setting = MapSetting(3, map={'dog': 1, 'bat': 2, 'cat': 3})
        self.assertEquals(setting.get_value(), 3)

    def test_map_setting_valid_choice(self):
        setting = MapSetting(3, map={'dog': 1, 'bat': 2, 'cat': 3})
        self.assertEquals(setting.get_value(), 3)
        setting.parse('bat')
        self.assertEquals(setting.get_value(), 2)

    def test_enum_setting_invalid_initialization(self):
        with self.assertRaises(MissingArgumentException):
            setting = EnumStringSetting('cat', wrong_argument=[0, 1, 2])

    # enum settings
    def test_enum_setting_invalid_initialization(self):
        with self.assertRaises(MissingArgumentException):
            setting = EnumStringSetting('cat', wrong_argument=[0, 1, 2])

    def test_enum_setting_invalid_default_value(self):
        with self.assertRaises(ValidationException):
            setting = EnumStringSetting(3, choices=[0, 1, 2])

    def test_enum_setting_invalid_choice(self):
        setting = EnumStringSetting(0, choices=[0, 1, 2])
        with self.assertRaises(ValidationException):
            setting.parse(3)

    def test_enum_setting_valid_default(self):
        setting = EnumStringSetting(3, choices=[1, 2, 3])
        self.assertEquals(setting.get_value(), 3)

    def test_enum_setting_valid_choice(self):
        setting = EnumStringSetting(3, choices=[1, 2, 3])
        self.assertEquals(setting.get_value(), 3)
        setting.parse(2)
        self.assertEquals(setting.get_value(), 2)

    # multiple choice settings
    def test_multiple_setting_invalid_initialization(self):
        with self.assertRaises(MissingArgumentException):
            setting = MultipleChoiceSetting(
                ['2'], wrong_argument=['0', '1', '2'])

    def test_multiple_setting_invalid_default_value(self):
        with self.assertRaises(ValidationException):
            setting = MultipleChoiceSetting(
                ['3', '4'], choices=['0', '1', '2'])

    def test_multiple_setting_invalid_choice(self):
        setting = MultipleChoiceSetting(['1', '2'], choices=['0', '1', '2'])
        with self.assertRaises(ValidationException):
            setting.parse('4, 3')

    def test_multiple_setting_valid_default(self):
        setting = MultipleChoiceSetting(['3'], choices=['1', '2', '3'])
        self.assertEquals(setting.get_value(), ['3'])

    def test_multiple_setting_valid_choice(self):
        setting = MultipleChoiceSetting(['3'], choices=['1', '2', '3'])
        self.assertEquals(setting.get_value(), ['3'])
        setting.parse('2')
        self.assertEquals(setting.get_value(), ['2'])

    # search language settings
    def test_lang_setting_valid_choice(self):
        setting = SearchLanguageSetting('en', choices=['de', 'en'])
        setting.parse('de')
        self.assertEquals(setting.get_value(), 'de')

    def test_lang_setting_invalid_choice(self):
        setting = SearchLanguageSetting('en', choices=['de', 'en'])
        setting.parse('xx')
        self.assertEquals(setting.get_value(), 'en')

    def test_lang_setting_old_cookie_choice(self):
        setting = SearchLanguageSetting('en', choices=['en', 'es', 'es-ES'])
        setting.parse('es_XA')
        self.assertEquals(setting.get_value(), 'es')

    def test_lang_setting_old_cookie_format(self):
        setting = SearchLanguageSetting('en', choices=['en', 'es', 'es-ES'])
        setting.parse('es_ES')
        self.assertEquals(setting.get_value(), 'es-ES')

    def test_lang_setting_old_default(self):
        setting = SearchLanguageSetting('en', choices=['en', 'es', 'de'])
        setting.parse('all')
        self.assertEquals(setting.get_value(), 'en')

    # plugins settings
    def test_plugins_setting_all_default_enabled(self):
        plugin1 = PluginStub('plugin1', True)
        plugin2 = PluginStub('plugin2', True)
        setting = PluginsSetting(['3'], choices=[plugin1, plugin2])
        self.assertEquals(setting.get_enabled(), set(['plugin1', 'plugin2']))

    def test_plugins_setting_few_default_enabled(self):
        plugin1 = PluginStub('plugin1', True)
        plugin2 = PluginStub('plugin2', False)
        plugin3 = PluginStub('plugin3', True)
        setting = PluginsSetting('name', choices=[plugin1, plugin2, plugin3])
        self.assertEquals(setting.get_enabled(), set(['plugin1', 'plugin3']))
