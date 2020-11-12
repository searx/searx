from functools import partial
from urllib.parse import urlencode, urlparse, urljoin, urlsplit

from starlette.templating import Jinja2Templates, _TemplateResponse
from starlette.background import BackgroundTask
from starlette.routing import NoMatchFound

from searx import brand, logger
from searx.languages import language_codes as languages
from searx.settings import (
    settings,
    default_theme, templates_path, themes, result_templates,
    static_path, static_files,
    global_favicons
)
from searx.preferences import Preferences, LANGUAGE_CODES
from searx.engines import (
    categories, engines, engine_shortcuts, get_engines_stats, initialize_engines
)
from searx.utils import match_language
from searx.webapp import _get_ordered_categories, rtl_locales, VERSION_STRING
from searx.web.i18n import get_translations
from searx.web.proxy import proxify, image_proxify, add_protocol


# Extract domain from url
def extract_domain(url):
    return urlparse(url)[1]


class SearxJinja2Templates(Jinja2Templates):

    def get_env(self, directory: str) -> "jinja2.Environment":
        env = super().get_env(directory)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.add_extension('jinja2.ext.loopcontrols')
        env.add_extension('jinja2.ext.i18n')
        env.filters['extract_domain'] = extract_domain
        return env

    def get_template_for_locale(self, name: str, locale: str) -> "jinja2.Template":
        overlay = self.env.overlay()
        overlay.install_gettext_translations(get_translations(locale), newstyle=True)
        return overlay.get_template(name)

    def TemplateResponse(
        self,
        name: str,
        context: dict,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background: BackgroundTask = None,
    ) -> _TemplateResponse:
        if "request" not in context:
            raise ValueError('context must include a "request" key')
        template = self.get_template_for_locale(name, context['request'].state.locale)
        return _TemplateResponse(
            template,
            context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )


templates = SearxJinja2Templates(directory=templates_path)


def get_current_theme_name(request, override=None):
    """Returns theme name.

    Checks in this order:
    1. override
    2. cookies
    3. settings"""

    if override and (override in themes or override == '__common__'):
        return override
    theme_name = request.query_params.get('theme', request.state.preferences.get_value('theme'))
    if theme_name not in themes:
        theme_name = default_theme
    return theme_name


def url_for_theme(request, endpoint, override_theme=None, **values):
    # starlette migration
    if '_external' in values:
        del values['_external']
    if 'filename' in values:
        values['path'] = values['filename']
        del values['filename']

    #
    if endpoint == 'static' and values.get('path'):
        theme_name = get_current_theme_name(request, override=override_theme)
        filename_with_theme = "themes/{}/{}".format(theme_name, values['path'])
        if filename_with_theme in static_files:
            values['path'] = filename_with_theme
    try:
        return request.url_for(endpoint, **values)
    except NoMatchFound:
        error_message = "url_for, endpoint='%s' not found (values=%s)" % (endpoint, str(values))
        logger.error(error_message)
        request.state.errors.append(error_message)
        return ''


def get_result_template(theme, template_name):
    themed_path = theme + '/result_templates/' + template_name
    if themed_path in result_templates:
        return themed_path
    return 'result_templates/' + template_name


def render(request,
           template_name,
           override_theme=None,
           status_code=200,
           headers: dict = None,
           media_type: str = None,
           **kwargs):
    disabled_engines = request.state.preferences.engines.get_disabled()

    enabled_categories = set(category for engine_name in engines
                             for category in engines[engine_name].categories
                             if (engine_name, category) not in disabled_engines)

    if 'categories' not in kwargs:
        kwargs['categories'] = [x for x in
                                _get_ordered_categories()
                                if x in enabled_categories]

    if 'autocomplete' not in kwargs:
        kwargs['autocomplete'] = request.state.preferences.get_value('autocomplete')

    locale = request.state.preferences.get_value('locale')

    if locale in rtl_locales and 'rtl' not in kwargs:
        kwargs['rtl'] = True

    kwargs['searx_version'] = VERSION_STRING
    kwargs['method'] = request.state.preferences.get_value('method')
    kwargs['safesearch'] = str(request.state.preferences.get_value('safesearch'))
    kwargs['language_codes'] = languages
    if 'current_language' not in kwargs:
        kwargs['current_language'] = match_language(request.state.preferences.get_value('language'),
                                                    LANGUAGE_CODES)

    # override url_for function in templates
    kwargs['url_for'] = partial(url_for_theme, request)
    kwargs['image_proxify'] = partial(image_proxify, request.url_for('image_proxy'))\
        if request.state.preferences.get_value('image_proxy') else add_protocol
    kwargs['proxify'] = proxify if settings.get('result_proxy', {}).get('url') else None
    kwargs['opensearch_url'] = request.url_for('opensearch') + '?' \
        + urlencode({'method': kwargs['method'], 'autocomplete': kwargs['autocomplete']})
    kwargs['get_result_template'] = get_result_template
    kwargs['theme'] = get_current_theme_name(request, override=override_theme)
    kwargs['template_name'] = template_name
    kwargs['cookies'] = request.cookies
    kwargs['errors'] = request.state.errors
    kwargs['instance_name'] = settings['general']['instance_name']
    kwargs['results_on_new_tab'] = request.state.preferences.get_value('results_on_new_tab')
    kwargs['preferences'] = request.state.preferences
    kwargs['brand'] = brand
    kwargs['scripts'] = set()
    kwargs['endpoint'] = 'results' if 'q' in kwargs else request.scope['path']
    for plugin in request.state.user_plugins:
        for script in plugin.js_dependencies:
            kwargs['scripts'].add(script)

    kwargs['styles'] = set()
    for plugin in request.state.user_plugins:
        for css in plugin.css_dependencies:
            kwargs['styles'].add(css)

    kwargs['request'] = request
    return templates.TemplateResponse('{}/{}'.format(kwargs['theme'], template_name),
                                      kwargs,
                                      status_code=status_code,
                                      headers=headers,
                                      media_type=media_type)
