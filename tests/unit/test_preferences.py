from searx.preferences import (EnumStringSetting, MapSetting, MissingArgumentException, SearchLanguageSetting,
                               MultipleChoiceSetting, PluginsSetting, ValidationException)
from searx.testing import SearxTestCase


class PluginStub(object):

    def __init__(self, id, default_on):
        self.id = id
        self.default_on = default_on


class TestSettings(SearxTestCase):
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
        setting = SearchLanguageSetting('all', choices=['all', 'de', 'en'])
        setting.parse('de')
        self.assertEquals(setting.get_value(), 'de')

    def test_lang_setting_invalid_choice(self):
        setting = SearchLanguageSetting('all', choices=['all', 'de', 'en'])
        setting.parse('xx')
        self.assertEquals(setting.get_value(), 'all')

    def test_lang_setting_old_cookie_choice(self):
        setting = SearchLanguageSetting('all', choices=['all', 'es', 'es-ES'])
        setting.parse('es_XA')
        self.assertEquals(setting.get_value(), 'es')

    def test_lang_setting_old_cookie_format(self):
        setting = SearchLanguageSetting('all', choices=['all', 'es', 'es-ES'])
        setting.parse('es_ES')
        self.assertEquals(setting.get_value(), 'es-ES')

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
