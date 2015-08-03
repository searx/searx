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
    def __init__(self):
        self._settings = dict()
        self._is_empty = True

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
    def validate_method(self, value):
        return value in ["GET", "POST"]

    def validate_locale(self, value):
        return value in settings["locales"]

    def validate_language(self, value):
        return value in (language[0] for language in language_codes)

    def deserialize_blocked_engines(self, value):
        return set(value.split("__"))

    def serialize_blocked_engines(self, value):
        return ','.join(value)

    def validate_blocked_engines(self, value):
        if not isinstance(value, set):
            raise TypeErrorInvalidSetting()
        for engine in value:
            if len(engine.split("__")) != 2:
                raise TypeErrorInvalidSetting()
