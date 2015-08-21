from searx import user_settings
from searx.testing import SearxTestCase


class TestUserSettingsBase(SearxTestCase):
    def test_newly_constructed_settings_object_is_empty(self):
        settings = user_settings.UserSettingsBase()
        self.assertTrue(settings.empty())

    def test_getting_unset_setting_raises_exception(self):
        settings = user_settings.UserSettingsBase()
        with self.assertRaises(user_settings.UnknownSetting):
            settings.get("language")

    def test_get_the_same_value_as_set(self):
        settings = user_settings.UserSettingsBase()
        settings.set("language", "en")
        self.assertEqual("en", settings.get("language"))

    def test_two_settings_are_restorable(self):
        settings = user_settings.UserSettingsBase()
        settings.set("language", "en")
        settings.set("name", "John Doe")
        self.assertEqual("en", settings.get("language"))
        self.assertEqual("John Doe", settings.get("name"))

    def test_single_verifier(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            def verify_age(self, value):
                return 0 <= value <= 99

        with self.assertRaises(Exception):
            settings = MyUserSettings()
            settings.set("age", -1)

        with self.assertRaises(Exception):
            settings = MyUserSettings()
            settings.set("age", "1")

        with self.assertRaises(Exception):
            settings = MyUserSettings()
            settings.set("age", 9000)

        settings = MyUserSettings()
        settings.set("age", 9)

    def test_multiple_verifiers(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            def verify_age(self, value):
                return 0 <= value <= 99

            def verify_name(self, value):
                return 1 <= len(value) <= 100

        settings = MyUserSettings()
        settings.set("age", 9)
        settings.set("name", "John Doe")

        with self.assertRaises(Exception):
            settings.set("name", 5)

    def test_custom_validator(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            defaults = {"foo": "John"}

            def validate_foo(self, value):
                return {0: "Dan", 1: "John", "John": "John"}[value]

        settings = MyUserSettings()
        self.assertEqual(settings.get("foo"), "John")
        settings.set("foo", 0)
        self.assertEqual(settings.get("foo"), "Dan")

    def test_proper_invalid_setting_exception_class(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            def verify_name(self, value):
                return 1 <= len(value) <= 100

        settings = MyUserSettings()
        with self.assertRaises(user_settings.InvalidSetting):
            settings.set("name", 5)

        with self.assertRaises(user_settings.TypeErrorInvalidSetting):
            settings.set("name", 5)

    def test_value_error_proper_exception_raised(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            def verify_name(self, value):
                return 1 <= len(value) <= 100

        settings = MyUserSettings()
        with self.assertRaises(user_settings.InvalidSetting):
            settings.set("name", "")

        with self.assertRaises(user_settings.ValueErrorInvalidSetting):
            settings.set("name", "")

    def test_after_value_is_set_should_not_be_empty(self):
        settings = user_settings.UserSettingsBase()
        settings.set("foo", "bar")
        self.assertFalse(settings.empty())

    def test_restore_empty_cookies_should_be_empty(self):
        settings = user_settings.UserSettingsBase()
        settings.restore_from_cookies({})
        self.assertTrue(settings.empty())

    def test_restore_non_empty_cookies_should_not_be_empty(self):
        settings = user_settings.UserSettingsBase()
        settings.restore_from_cookies({"foo": "bar"})
        self.assertFalse(settings.empty())

    def test_export_settings_then_restore_the_same_string(self):
        to_export_from = user_settings.UserSettingsBase()
        to_export_from.set("name", "John Doe")
        cookies = {}
        to_export_from.save_to_cookies(cookies)
        to_import_to = user_settings.UserSettingsBase()
        to_import_to.restore_from_cookies(cookies)
        self.assertEqual(to_import_to.get("name"), "John Doe")

    def test_export_various_values_and_restore_them(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            def deserialize_age(self, value):
                return int(value)

            def serialize_owns(self, value):
                return ','.join(value)

            def deserialize_owns(self, value):
                return set(value.split(','))

        to_export_from = MyUserSettings()
        to_export_from.set("name", "John Doe")
        to_export_from.set("age", 32)
        to_export_from.set("owns", {"foo", "bar", })
        cookies = {}
        to_export_from.save_to_cookies(cookies)
        to_import_to = MyUserSettings()
        to_import_to.restore_from_cookies(cookies)
        self.assertEqual(to_import_to.get("name"), "John Doe")
        self.assertEqual(to_import_to.get("age"), 32)
        self.assertEqual(to_import_to.get("owns"), {"foo", "bar", })

    def test_save_to_cookies_should_only_use_strings(self):
        to_export_from = user_settings.UserSettingsBase()
        to_export_from.set("name", "John Doe")
        to_export_from.set("age", 32)
        to_export_from.set("owns", {"foo", "bar", })
        cookies = {}
        to_export_from.save_to_cookies(cookies)
        for value in cookies.values():
            self.assertIsInstance(value, str)

    def test_defaults(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            defaults = {"foo": "bar"}

        settings = MyUserSettings()
        self.assertEqual(settings.get("foo"), "bar")

    def test_override_from_form(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            defaults = {"foo": "bar", "bar": "Hello World"}

        settings = MyUserSettings()
        self.assertEqual(settings.get("foo"), "bar")
        self.assertEqual(settings.get("bar"), "Hello World")
        settings.override_from_form([
            ("foo", "baz", ),
            ("bar", "", ),
        ])
        self.assertEqual(settings.get("foo"), "baz")
        self.assertEqual(settings.get("bar"), "")

    def test_override_from_form_collection_fields(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            defaults = {"foo": "bar", "bars": set()}
            _collection_fields = {"bar": "bars"}

        settings = MyUserSettings()
        self.assertEqual(settings.get("foo"), "bar")
        self.assertEqual(settings.get("bars"), set())
        settings.override_from_form([
            ("foo", "baz", ),
            ("bar_x", "x", ),
            ("bar_y", "x", ),
        ])
        self.assertEqual(settings.get("foo"), "baz")
        self.assertEqual(settings.get("bars"), {"x", "y", })


class TestUserSettings(SearxTestCase):
    def simulate_http_cookie_handling(self, cookies):
        new_dict = dict()
        for key, value in cookies.iteritems():
            if type(key) == str and type(value) == str:
                new_dict[key] = value
        return new_dict

    def setUp(self):
        self._settings = user_settings.UserSettings()

    def test_method(self):
        self._settings.set("method", "POST")
        self._settings.set("method", "GET")

        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("method", "SET")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("method", 3.14)

    def test_locale(self):
        self._settings.get("locale")
        self._settings.set("locale", "en")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("locale", "English")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("locale", 55)
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("locale", None)

    def test_language(self):
        self._settings.get("language")
        self._settings.set("language", "en_US")
        self._settings.set("language", "all")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("language", "English")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("language", 55)
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("language", None)

    def test_blocked_engines_empty_set(self):
        self._settings.set("blocked_engines", set())
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies = self.simulate_http_cookie_handling(cookies)
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
        self.assertEqual(new_settings.get("blocked_engines"), set())

    def test_blocked_engines_single_item(self):
        self._settings.set("blocked_engines", {"google__general", })
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies = self.simulate_http_cookie_handling(cookies)
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
        self.assertEqual(new_settings.get(
            "blocked_engines"), {"google__general", })

    def test_blocked_engines_multiple_items(self):
        self._settings.set(
            "blocked_engines", {"google__general", "bing__general", })
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies = self.simulate_http_cookie_handling(cookies)
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
        self.assertEqual(new_settings.get("blocked_engines"),
                         {"google__general", "bing__general", })

    def test_blocked_engines_invalid_settings(self):
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("blocked_engines", "google__general")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("blocked_engines", {5, "bing__general", })
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("blocked_engines", {"bing_general", })

    def test_theme(self):
        self._settings.get("theme")
        self._settings.set("theme", "foobar")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("theme", 55)
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("theme", None)
        self._settings.set("theme", u"courgette")
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies = self.simulate_http_cookie_handling(cookies)
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
        self.assertEqual(new_settings.get("theme"), u"courgette")

    def test_allowed_plugins_empty_set(self):
        self._settings.set("allowed_plugins", set())
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies = self.simulate_http_cookie_handling(cookies)
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
        self.assertEqual(new_settings.get("allowed_plugins"), set())

    def test_allowed_plugins_single_item(self):
        self._settings.set("allowed_plugins", {"google__general", })
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies = self.simulate_http_cookie_handling(cookies)
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
        self.assertEqual(new_settings.get(
            "allowed_plugins"), {"google__general", })

    def test_allowed_plugins_multiple_items(self):
        self._settings.set(
            "allowed_plugins", {"google__general", "bing__general", })
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies = self.simulate_http_cookie_handling(cookies)
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
        self.assertEqual(new_settings.get("allowed_plugins"),
                         {"google__general", "bing__general", })

    def test_allowed_plugins_invalid_settings(self):
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("allowed_plugins", "google__general")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("allowed_plugins", {5, "bing__general", })

    def test_disabled_plugins_single_item(self):
        self._settings.set("disabled_plugins", {"google__general", })
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies = self.simulate_http_cookie_handling(cookies)
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
        self.assertEqual(new_settings.get(
            "disabled_plugins"), {"google__general", })

    def test_disabled_plugins_multiple_items(self):
        self._settings.set(
            "disabled_plugins", {"google__general", "bing__general", })
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies = self.simulate_http_cookie_handling(cookies)
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
        self.assertEqual(new_settings.get("disabled_plugins"),
                         {"google__general", "bing__general", })

    def test_disabled_plugins_defaults(self):
        self.assertEqual(self._settings.get("disabled_plugins"), set())

    def test_allowed_plugins_defaults(self):
        self.assertEqual(self._settings.get("allowed_plugins"), set())

    def test_disabled_plugins_invalid_settings(self):
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("disabled_plugins", "foo bar")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("disabled_plugins", {5, "foo_bar", })

    def test_categories(self):
        self._settings.get("categories")

        self._settings.set(
            "categories", {"foo", "bar", "general", })
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies = self.simulate_http_cookie_handling(cookies)
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
        self.assertEqual(new_settings.get("categories"),
                         {"foo", "bar", "general", })

    def test_safesearch(self):
        self._settings.get("safesearch")
        self._settings.set("safesearch", "1")
        self._settings.set("safesearch", u"1")
        self._settings.set("safesearch", "2")
        self._settings.set("safesearch", u"2")
        self._settings.set("safesearch", "0")
        self._settings.set("safesearch", u"0")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("safesearch", "-3")
            self._settings.set("safesearch", u"-3")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("safesearch", "3")
            self._settings.set("safesearch", u"3")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("safesearch", "")
            self._settings.set("safesearch", u"")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("safesearch", None)

    def test_image_proxy(self):
        self._settings.get("image_proxy")
        self._settings.set("image_proxy", None)
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("image_proxy", 4564564)
        self._settings.set("image_proxy", "1")
        self._settings.set("image_proxy", "0")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("image_proxy", "foo bar")
        self._settings.form_set("image_proxy", "")

    def test_image_proxy_empty_string(self):
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies["image_proxy"] = u""
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)

    def test_autocomplete(self):
        self._settings.get("autocomplete")
        self._settings.set("autocomplete", None)
        self._settings.set("autocomplete", "google")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("autocomplete", 4564564)
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("autocomplete", "https://pro.xy")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("autocomplete", "foo bar")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("autocomplete", "")

    def test_autocomplete_empty_string(self):
        cookies = dict()
        self._settings.save_to_cookies(cookies)
        cookies["autocomplete"] = u""
        new_settings = user_settings.UserSettings()
        new_settings.restore_from_cookies(cookies)
