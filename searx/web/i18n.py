from functools import partial, lru_cache

from babel import dates, numbers, support, Locale

from searx.settings import searx_dir, settings
from searx.utils import match_language
from searx import logger


translation_directory = searx_dir + "/translations"


def _get_browser_or_settings_language(request, lang_list):
    for lang in request.headers.get("Accept-Language", "en").split(","):
        if ';' in lang:
            lang = lang.split(';')[0]
        locale = match_language(lang, lang_list, fallback=None)
        if locale is not None:
            return locale
    return settings['search']['default_lang'] or 'en'


def get_babel_locale(locale):
    #
    if locale == 'zh_TW':
        return 'zh_Hant_TW'

    # see _get_translations function
    # and https://github.com/searx/searx/pull/1863
    if locale == 'oc':
        return 'fr_FR'

    return locale


@lru_cache(maxsize=None)
def load_translation(locale_str):
    locale = Locale.parse(locale_str)
    return support.Translations.load(translation_directory, [locale], 'messages')


def get_translations(locale_str):
    """Returns the correct gettext translations that should be used for
    this request.  This will never fail and return a dummy translation
    object if used outside of the request or if a translation cannot be
    found.
    """
    if locale_str is None:
        return support.NullTranslations()

    translations = load_translation(get_babel_locale(locale_str))
    print('translation', translations, 'for', locale_str, 'gettext("files")', translations.gettext('files'))
    return translations


def gettext(string: str, locale_str: str = None, **variables) -> str:
    """Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string.

    ::

        gettext('Hello World!')
        gettext('Hello %(name)s!', name='World')
    """
    if locale_str is None:
        return string if not variables else string % variables
    s = get_translations(locale_str).gettext(string)
    return s if not variables else s % variables
