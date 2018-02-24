from searx.preferences import (EnumStringSetting, MapSetting, MissingArgumentException, SearchLanguageSetting,
                               MultipleChoiceSetting, PluginsSetting, ValidationException)
from searx.preferences import Preferences
from searx.testing import SearxTestCase
from searx.engines import engines
from mock import patch, Mock

# def get_multiple_choice_setting_mock(default_value, **kwargs):
#     return Mock(value=default_value, **kwargs)

# def get_search_language_setting_mock(default_value):
#     return Mock(value=default_value, choices="en-US")

# def get_enum_string_setting_mock(default_value, **kwargs):
#     return Mock(value=default_value, **kwargs)

# def get_map_setting_mock(default_value, **kwargs):
#     return Mock(value=default_value, **kwargs)

# def get_plugin_setting_mock():
#     plugin1 = PluginStub('plugin1', True)
#     plugin2 = PluginStub('plugin2', False)
#     plugin3 = PluginStub('plugin3', True)
#     return PluginsSetting('name', choices=[plugin1, plugin2, plugin3])

class PluginStub(object):

    def __init__(self, id, default_on):
        self.id = id
        self.default_on = default_on

# class PreferencesStub(object):
#     def __init__(self, key_value_settings, engines, plugins):
#         super(PreferencesStub, self).__init__()

#         self.key_value_settings = key_value_settings
#         self.engines = engines
#         self.plugins = plugins
#         self.unknown_params = {}

class TestSettings(SearxTestCase):

    @patch('searx.preferences.MultipleChoiceSetting')
    @patch('searx.preferences.EnumStringSetting')
    @patch('searx.preferences.MapSetting')
    @patch('searx.preferences.PluginsSetting')
    @patch('searx.preferences.SearchLanguageSetting')
    def test_preferences(self, sl_setting_mock, plugin_setting_mock, map_setting_mock, enum_setting_mock, mc_setting_mock):
        preferences = Preferences(['oscar'], ['general'], engines, [PluginStub(1, False)])

        sl_setting_mock.assert_called_once()
        plugin_setting_mock.assert_called_once()
        map_setting_mock.assert_called_once

        self.assertEquals(mc_setting_mock.call_count, 2)
        self.assertEquals(enum_setting_mock.call_count, 4)

        print(preferences.key_value_settings['language'])

        # mock_key_value_settings = {
        #     'categories': get_multiple_choice_setting_mock(['general']),
        #     'language': get_search_language_setting_mock('en-US'),
        #     'locale': get_enum_string_setting_mock(''),
        #     'autocomplete': get_enum_string_setting_mock(''),
        #     'image_proxy': get_map_setting_mock(False),
        #     'method': get_enum_string_setting_mock('POST'),
        #     'safesearch': get_map_setting_mock(0),
        #     'theme': get_enum_string_setting_mock('oscar'),
        #     'results_on_new_tab': get_map_setting_mock(False),
        #     'doi_resolver': get_multiple_choice_setting_mock(['oadoi.org'])
        # }

        # # engines = 
        # plugins = get_plugin_setting_mock()

        # prefereces = PreferencesStub(mock_key_value_settings, None, plugins)

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
            setting = MultipleChoiceSetting(['2'], wrong_argument=['0', '1', '2'])

    def test_multiple_setting_invalid_default_value(self):
        with self.assertRaises(ValidationException):
            setting = MultipleChoiceSetting(['3', '4'], choices=['0', '1', '2'])

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
