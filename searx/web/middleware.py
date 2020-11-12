from time import time
from functools import partial

from starlette.requests import HTTPConnection
from starlette.middleware import Middleware

from searx import logger
from searx.preferences import Preferences, ValidationException, LANGUAGE_CODES
from searx.plugins import plugins
from searx.settings import (
    settings, searx_debug,
    default_theme, templates_path, themes, result_templates,
    static_path, static_files,
    global_favicons
)
from searx.engines import (
    categories, engines, engine_shortcuts, get_engines_stats, initialize_engines
)
from searx.utils import html_to_text, gen_useragent, dict_subset, match_language
from searx.web.i18n import gettext


def _get_browser_or_settings_language(request, lang_list):
    for lang in request.headers.get("Accept-Language", "en").split(","):
        if ';' in lang:
            lang = lang.split(';')[0]
        locale = match_language(lang, lang_list, fallback=None)
        if locale is not None:
            return locale
    return settings['search']['default_lang'] or 'en'


async def pre_request(request):
    request.state.time_started = time()
    request.state.timings = []
    request.state.errors = []

    preferences = Preferences(themes, list(categories.keys()), engines, plugins)
    request.state.preferences = preferences

    # special case for webkit & android
    user_agent = request.headers.get('User-Agent', '').lower()
    if 'webkit' in user_agent and 'android' in user_agent:
        preferences.key_value_settings['method'].value = 'GET'

    # parse cookies
    try:
        preferences.parse_dict(request.cookies)
    except:
        request.state.errors.append(gettext('Invalid settings, please edit your preferences'))

    # merge GET, POST vars
    # request.form
    request.state.form = dict(await request.form())
    for k, v in request.query_params.items():
        if k not in request.state.form:
            request.state.form[k] = v

    # preferences parameters
    if request.state.form.get('preferences'):
        preferences.parse_encoded_data(request.state.form['preferences'])
    else:
        try:
            preferences.parse_dict(request.state.form)
        except Exception as e:
            logger.exception('invalid settings')
            request.state.errors.append(gettext('Invalid settings'))

    # initialize locale first
    locale = preferences.get_value("locale")
    if not locale:
        locale = _get_browser_or_settings_language(request, settings['locales'].keys())
        preferences.parse_dict({"locale": locale})
    request.state.locale = locale
    request.state.gettext = partial(gettext, locale_str=locale)

    # init search language and locale
    if not preferences.get_value("language"):
        preferences.parse_dict({"language": _get_browser_or_settings_language(request, LANGUAGE_CODES)})

    # request.user_plugins
    request.state.user_plugins = []
    allowed_plugins = preferences.plugins.get_enabled()
    disabled_plugins = preferences.plugins.get_disabled()
    for plugin in plugins:
        if ((plugin.default_on and plugin.id not in disabled_plugins)
                or plugin.id in allowed_plugins):
            request.state.user_plugins.append(plugin)
