from searx import settings
from searx.languages import language_codes
from searx.autocomplete import backends as autocomplete_backends
from searx import utils


class UnknownSetting(Exception):
    pass


class InvalidSetting(Exception):
    pass


class ValueErrorInvalidSetting(InvalidSetting):
    pass


class TypeErrorInvalidSetting(InvalidSetting):
    pass


class UserSettingsBase(object):
    defaults = None
    _collection_fields = {}

    def __init__(self):
        self._settings = dict()
        self._is_empty = True
        if self.defaults is None:
            self.defaults = dict()
        self._load_defaults()

    def __repr__(self):
        return repr(self._settings)

    def _load_defaults(self):
        self.restore_from_cookies(self.defaults)

    def empty(self):
        return self._is_empty

    def get(self, setting):
        if setting in self._settings:
            return self._settings[setting]
        else:
            raise UnknownSetting()

    def verify(self, setting, value):
        try:
            if hasattr(self, "verify_%s" % setting) and \
               not getattr(self, "verify_%s" % setting)(value):
                raise ValueErrorInvalidSetting((setting, value))
        except TypeError:
            raise TypeErrorInvalidSetting((setting, value))

    def validate(self, setting, value):
        if hasattr(self, "validate_%s" % setting):
            return getattr(self, "validate_%s" % setting)(value)
        else:
            self.verify(setting, value)
            return value

    def set(self, setting, value):
        self._settings[setting] = self.validate(setting, value)
        self._is_empty = False

    def form_set(self, setting, value):
        self.set(setting, self._deserialize(setting, value))

    def override_from_form(self, form_data):
        form_data = utils.parse_form(form_data, self._collection_fields)
        for field, value in form_data.iteritems():
            if field in self._collection_fields.values():
                self.set(field, value)
            else:
                self.form_set(field, value)

    def _serialize(self, setting, value):
        if hasattr(self, "serialize_%s" % setting):
            return getattr(self, "serialize_%s" % setting)(value)
        else:
            return str(value)

    def _deserialize(self, setting, value):
        if hasattr(self, "deserialize_%s" % setting):
            return getattr(self, "deserialize_%s" % setting)(value)
        else:
            return value

    def restore_from_cookies(self, cookies):
        for setting, value in cookies.iteritems():
            self.set(setting, self._deserialize(setting, value))

    def save_to_cookies(self, cookies):
        cookies.update(
            {setting: self._serialize(setting, value) for setting, value in self._settings.iteritems()}
        )

    def save_to_response(self, resp, cookie_max_age):
        cookies = dict()
        self.save_to_cookies(cookies)
        for key, value in cookies.iteritems():
            resp.set_cookie(key, value, max_age=cookie_max_age)


class UserSettings(UserSettingsBase):
    defaults = {
        "disabled_plugins": set(), "allowed_plugins": set(),
        "blocked_engines": set(), "method": "POST", "safesearch": "1",
        "categories": "", "locale": "en", "language": "all",
        "theme": settings['server'].get('default_theme', 'default'),
        "image_proxy": None, "autocomplete": None, }
    _collection_fields = {
        "category": "categories", "engine": "blocked_engines", "plugin": "plugins"
    }

    def _load_defaults(self):
        super(UserSettings, self)._load_defaults()
        self.load_default_locale()

    def load_default_locale(self):
        if settings['server'].get('default_locale'):
            self.set("locale", settings['server']['default_locale'])

    def verify_method(self, value):
        return value in ["GET", "POST"]

    def verify_locale(self, value):
        return value in settings["locales"]

    def verify_language(self, value):
        if value == "all":
            return True
        else:
            return value in (language[0] for language in language_codes)

    def serialize_blocked_engines(self, value):
        return ",".join(set(value))

    def deserialize_blocked_engines(self, value):
        if value:
            return set(value.split(","))
        else:
            return set()

    def verify_blocked_engines(self, value):
        if not isinstance(value, set):
            raise TypeErrorInvalidSetting()
        for engine in value:
            if not (isinstance(engine, str) or isinstance(engine, unicode)):
                raise TypeErrorInvalidSetting()
            if len(engine.split("__")) != 2:
                raise ValueErrorInvalidSetting()
        return True

    def serialize_allowed_plugins(self, value):
        return ",".join(set(value))

    def deserialize_allowed_plugins(self, value):
        if value:
            return set(value.split(","))
        else:
            return set()

    def verify_allowed_plugins(self, value):
        if not isinstance(value, set):
            raise TypeErrorInvalidSetting()
        for engine in value:
            if not isinstance(engine, str):
                raise TypeErrorInvalidSetting()
        return True

    def serialize_disabled_plugins(self, value):
        return ",".join(set(value))

    def deserialize_disabled_plugins(self, value):
        if value:
            return set(value.split(","))
        else:
            return set()

    def verify_disabled_plugins(self, value):
        if not isinstance(value, set):
            raise TypeErrorInvalidSetting()
        for engine in value:
            if not isinstance(engine, str):
                raise TypeErrorInvalidSetting()
        return True

    def serialize_categories(self, value):
        return ",".join(set(value))

    def deserialize_categories(self, value):
        if value:
            return set(value.split(","))
        else:
            return set()

    def verify_categories(self, value):
        if not isinstance(value, set):
            raise TypeErrorInvalidSetting(value)
        for engine in value:
            if not (isinstance(engine, str) or isinstance(engine, unicode)):
                raise TypeErrorInvalidSetting(value)
        return True

    def verify_theme(self, value):
        if not (isinstance(value, str) or isinstance(value, unicode)):
            raise TypeErrorInvalidSetting(repr(value))
        return True

    def verify_safesearch(self, value):
        return str(value) in {"0", "1", "2", }

    def verify_image_proxy(self, value):
        if value is None:
            return True
        try:
            return int(value) in [0, 1]
        except ValueError:
            raise ValueErrorInvalidSetting()

    def deserialize_image_proxy(self, value):
        if value == "None" or value == "":
            return None
        else:
            return value

    def verify_autocomplete(self, value):
        if value is None:
            return True
        return value in autocomplete_backends

    def deserialize_autocomplete(self, value):
        if value == "None" or value == "":
            return None
        else:
            return value
