from searx import settings
from searx.languages import language_codes


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

    def __init__(self):
        self._settings = dict()
        self._is_empty = True
        if self.defaults is None:
            self.defaults = dict()
        self.restore_from_cookies(self.defaults)

    def empty(self):
        return self._is_empty

    def get(self, setting):
        if setting in self._settings:
            return self._settings[setting]
        else:
            raise UnknownSetting()

    def validate(self, setting, value):
        try:
            if hasattr(self, "validate_%s" % setting) and \
               not getattr(self, "validate_%s" % setting)(value):
                raise ValueErrorInvalidSetting()
        except TypeError:
            raise TypeErrorInvalidSetting()

    def set(self, setting, value):
            self.validate(setting, value)
            self._settings[setting] = value
            self._is_empty = False

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


class UserSettings(UserSettingsBase):
    defaults = {"disabled_plugins": set(), "allowed_plugins": set(), }

    def validate_method(self, value):
        return value in ["GET", "POST"]

    def validate_locale(self, value):
        return value in settings["locales"]

    def validate_language(self, value):
        return value in (language[0] for language in language_codes)

   def serialize_blocked_engines(self, value):
        return ",".join(set(value))

    def deserialize_blocked_engines(self, value):
        if value:
            return set(value.split(","))
        else:
            return set()

    def validate_blocked_engines(self, value):
        if not isinstance(value, set):
            raise TypeErrorInvalidSetting()
        for engine in value:
            if not isinstance(engine, str):
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

    def validate_allowed_plugins(self, value):
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

    def validate_disabled_plugins(self, value):
        if not isinstance(value, set):
            raise TypeErrorInvalidSetting()
        for engine in value:
            if not isinstance(engine, str):
                raise TypeErrorInvalidSetting()
        return True

    def validate_theme(self, value):
        if not isinstance(value, str):
            raise TypeErrorInvalidSetting()
        return True
