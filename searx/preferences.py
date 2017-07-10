from searx import settings, autocomplete
from searx.languages import language_codes as languages
from searx.url_utils import urlencode


COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 5  # 5 years
LANGUAGE_CODES = [l[0] for l in languages]
LANGUAGE_CODES.append('all')
DISABLED = 0
ENABLED = 1


class MissingArgumentException(Exception):
    pass


class ValidationException(Exception):
    pass


class Setting(object):
    """Base class of user settings"""

    def __init__(self, default_value, **kwargs):
        super(Setting, self).__init__()
        self.value = default_value
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._post_init()

    def _post_init(self):
        pass

    def parse(self, data):
        self.value = data

    def get_value(self):
        return self.value

    def save(self, name, resp):
        resp.set_cookie(name, self.value, max_age=COOKIE_MAX_AGE)


class StringSetting(Setting):
    """Setting of plain string values"""
    pass


class EnumStringSetting(Setting):
    """Setting of a value which can only come from the given choices"""

    def _validate_selection(self, selection):
        if selection not in self.choices:
            raise ValidationException('Invalid value: "{0}"'.format(selection))

    def _post_init(self):
        if not hasattr(self, 'choices'):
            raise MissingArgumentException('Missing argument: choices')
        self._validate_selection(self.value)

    def parse(self, data):
        self._validate_selection(data)
        self.value = data


class MultipleChoiceSetting(EnumStringSetting):
    """Setting of values which can only come from the given choices"""

    def _validate_selections(self, selections):
        for item in selections:
            if item not in self.choices:
                raise ValidationException('Invalid value: "{0}"'.format(selections))

    def _post_init(self):
        if not hasattr(self, 'choices'):
            raise MissingArgumentException('Missing argument: choices')
        self._validate_selections(self.value)

    def parse(self, data):
        if data == '':
            self.value = []
            return

        elements = data.split(',')
        self._validate_selections(elements)
        self.value = elements

    def parse_form(self, data):
        self.value = []
        for choice in data:
            if choice in self.choices and choice not in self.value:
                self.value.append(choice)

    def save(self, name, resp):
        resp.set_cookie(name, ','.join(self.value), max_age=COOKIE_MAX_AGE)


class SearchLanguageSetting(EnumStringSetting):
    """Available choices may change, so user's value may not be in choices anymore"""

    def parse(self, data):
        if data not in self.choices and data != self.value:
            # hack to give some backwards compatibility with old language cookies
            data = str(data).replace('_', '-')
            lang = data.split('-')[0]
            if data in self.choices:
                pass
            elif lang in self.choices:
                data = lang
            elif data == 'nb-NO':
                data = 'no-NO'
            elif data == 'ar-XA':
                data = 'ar-SA'
            else:
                data = self.value
        self.value = data


class MapSetting(Setting):
    """Setting of a value that has to be translated in order to be storable"""

    def _post_init(self):
        if not hasattr(self, 'map'):
            raise MissingArgumentException('missing argument: map')
        if self.value not in self.map.values():
            raise ValidationException('Invalid default value')

    def parse(self, data):
        if data not in self.map:
            raise ValidationException('Invalid choice: {0}'.format(data))
        self.value = self.map[data]
        self.key = data

    def save(self, name, resp):
        if hasattr(self, 'key'):
            resp.set_cookie(name, self.key, max_age=COOKIE_MAX_AGE)


class SwitchableSetting(Setting):
    """ Base class for settings that can be turned on && off"""

    def _post_init(self):
        self.disabled = set()
        self.enabled = set()
        if not hasattr(self, 'choices'):
            raise MissingArgumentException('missing argument: choices')

    def transform_form_items(self, items):
        return items

    def transform_values(self, values):
        return values

    def parse_cookie(self, data):
        if data[DISABLED] != '':
            self.disabled = set(data[DISABLED].split(','))
        if data[ENABLED] != '':
            self.enabled = set(data[ENABLED].split(','))

    def parse_form(self, items):
        items = self.transform_form_items(items)

        self.disabled = set()
        self.enabled = set()
        for choice in self.choices:
            if choice['default_on']:
                if choice['id'] in items:
                    self.disabled.add(choice['id'])
            else:
                if choice['id'] not in items:
                    self.enabled.add(choice['id'])

    def save(self, resp):
        resp.set_cookie('disabled_{0}'.format(self.value), ','.join(self.disabled), max_age=COOKIE_MAX_AGE)
        resp.set_cookie('enabled_{0}'.format(self.value), ','.join(self.enabled), max_age=COOKIE_MAX_AGE)

    def get_disabled(self):
        disabled = self.disabled
        for choice in self.choices:
            if not choice['default_on'] and choice['id'] not in self.enabled:
                disabled.add(choice['id'])
        return self.transform_values(disabled)

    def get_enabled(self):
        enabled = self.enabled
        for choice in self.choices:
            if choice['default_on'] and choice['id'] not in self.disabled:
                enabled.add(choice['id'])
        return self.transform_values(enabled)


class EnginesSetting(SwitchableSetting):

    def _post_init(self):
        super(EnginesSetting, self)._post_init()
        transformed_choices = []
        for engine_name, engine in self.choices.items():
            for category in engine.categories:
                transformed_choice = dict()
                transformed_choice['default_on'] = not engine.disabled
                transformed_choice['id'] = '{}__{}'.format(engine_name, category)
                transformed_choices.append(transformed_choice)
        self.choices = transformed_choices

    def transform_form_items(self, items):
        return [item[len('engine_'):].replace('_', ' ').replace('  ', '__') for item in items]

    def transform_values(self, values):
        if len(values) == 1 and next(iter(values)) == '':
            return list()
        transformed_values = []
        for value in values:
            engine, category = value.split('__')
            transformed_values.append((engine, category))
        return transformed_values


class PluginsSetting(SwitchableSetting):

    def _post_init(self):
        super(PluginsSetting, self)._post_init()
        transformed_choices = []
        for plugin in self.choices:
            transformed_choice = dict()
            transformed_choice['default_on'] = plugin.default_on
            transformed_choice['id'] = plugin.id
            transformed_choices.append(transformed_choice)
        self.choices = transformed_choices

    def transform_form_items(self, items):
        return [item[len('plugin_'):] for item in items]


class Preferences(object):
    """Validates and saves preferences to cookies"""

    def __init__(self, themes, categories, engines, plugins):
        super(Preferences, self).__init__()

        self.key_value_settings = {'categories': MultipleChoiceSetting(['general'], choices=categories),
                                   'language': SearchLanguageSetting(settings['search']['language'],
                                                                     choices=LANGUAGE_CODES),
                                   'locale': EnumStringSetting(settings['ui']['default_locale'],
                                                               choices=list(settings['locales'].keys()) + ['']),
                                   'autocomplete': EnumStringSetting(settings['search']['autocomplete'],
                                                                     choices=list(autocomplete.backends.keys()) + ['']),
                                   'image_proxy': MapSetting(settings['server']['image_proxy'],
                                                             map={'': settings['server']['image_proxy'],
                                                                  '0': False,
                                                                  '1': True,
                                                                  'True': True,
                                                                  'False': False}),
                                   'method': EnumStringSetting('POST', choices=('GET', 'POST')),
                                   'safesearch': MapSetting(settings['search']['safe_search'], map={'0': 0,
                                                                                                    '1': 1,
                                                                                                    '2': 2}),
                                   'theme': EnumStringSetting(settings['ui']['default_theme'], choices=themes),
                                   'results_on_new_tab': MapSetting(False, map={'0': False,
                                                                                '1': True,
                                                                                'False': False,
                                                                                'True': True})}

        self.engines = EnginesSetting('engines', choices=engines)
        self.plugins = PluginsSetting('plugins', choices=plugins)
        self.unknown_params = {}

    def get_as_url_params(self):
        settings_kv = {}
        for k, v in self.key_value_settings.items():
            if isinstance(v, MultipleChoiceSetting):
                settings_kv[k] = ','.join(v.get_value())
            else:
                settings_kv[k] = v.get_value()

        settings_kv['disabled_engines'] = ','.join(self.engines.disabled)
        settings_kv['enabled_engines'] = ','.join(self.engines.enabled)

        settings_kv['disabled_plugins'] = ','.join(self.plugins.disabled)
        settings_kv['enabled_plugins'] = ','.join(self.plugins.enabled)

        return urlencode(settings_kv)

    def parse_dict(self, input_data):
        for user_setting_name, user_setting in input_data.items():
            if user_setting_name in self.key_value_settings:
                self.key_value_settings[user_setting_name].parse(user_setting)
            elif user_setting_name == 'disabled_engines':
                self.engines.parse_cookie((input_data.get('disabled_engines', ''),
                                           input_data.get('enabled_engines', '')))
            elif user_setting_name == 'disabled_plugins':
                self.plugins.parse_cookie((input_data.get('disabled_plugins', ''),
                                           input_data.get('enabled_plugins', '')))

    def parse_form(self, input_data):
        disabled_engines = []
        enabled_categories = []
        disabled_plugins = []
        for user_setting_name, user_setting in input_data.items():
            if user_setting_name in self.key_value_settings:
                self.key_value_settings[user_setting_name].parse(user_setting)
            elif user_setting_name.startswith('engine_'):
                disabled_engines.append(user_setting_name)
            elif user_setting_name.startswith('category_'):
                enabled_categories.append(user_setting_name[len('category_'):])
            elif user_setting_name.startswith('plugin_'):
                disabled_plugins.append(user_setting_name)
            else:
                self.unknown_params[user_setting_name] = user_setting
        self.key_value_settings['categories'].parse_form(enabled_categories)
        self.engines.parse_form(disabled_engines)
        self.plugins.parse_form(disabled_plugins)

    # cannot be used in case of engines or plugins
    def get_value(self, user_setting_name):
        if user_setting_name in self.key_value_settings:
            return self.key_value_settings[user_setting_name].get_value()

    def save(self, resp):
        for user_setting_name, user_setting in self.key_value_settings.items():
            user_setting.save(user_setting_name, resp)
        self.engines.save(resp)
        self.plugins.save(resp)
        for k, v in self.unknown_params.items():
            resp.set_cookie(k, v, max_age=COOKIE_MAX_AGE)
        return resp
