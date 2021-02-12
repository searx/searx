
'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2013- by Adam Tauber, <asciimoo@gmail.com>
'''

import sys
import threading
from os.path import realpath, dirname
from babel.localedata import locale_identifiers
from urllib.parse import urlparse
from operator import itemgetter
from searx import settings
from searx import logger
from searx.data import ENGINES_LANGUAGES
from searx.poolrequests import get, get_proxy_cycles
from searx.utils import load_module, match_language, get_engine_from_settings


logger = logger.getChild('engines')

engine_dir = dirname(realpath(__file__))

engines = {}

categories = {'general': []}

babel_langs = [lang_parts[0] + '-' + lang_parts[-1] if len(lang_parts) > 1 else lang_parts[0]
               for lang_parts in (lang_code.split('_') for lang_code in locale_identifiers())]

engine_shortcuts = {}
engine_default_args = {'paging': False,
                       'categories': ['general'],
                       'supported_languages': [],
                       'safesearch': False,
                       'timeout': settings['outgoing']['request_timeout'],
                       'shortcut': '-',
                       'disabled': False,
                       'time_range_support': False,
                       'engine_type': 'online',
                       'display_error_messages': True,
                       'tokens': []}


def load_engine(engine_data):
    engine_name = engine_data['name']
    if '_' in engine_name:
        logger.error('Engine name contains underscore: "{}"'.format(engine_name))
        sys.exit(1)

    if engine_name.lower() != engine_name:
        logger.warn('Engine name is not lowercase: "{}", converting to lowercase'.format(engine_name))
        engine_name = engine_name.lower()
        engine_data['name'] = engine_name

    engine_module = engine_data['engine']

    try:
        engine = load_module(engine_module + '.py', engine_dir)
    except (SyntaxError, KeyboardInterrupt, SystemExit, SystemError, ImportError, RuntimeError):
        logger.exception('Fatal exception in engine "{}"'.format(engine_module))
        sys.exit(1)
    except:
        logger.exception('Cannot load engine "{}"'.format(engine_module))
        return None

    for param_name, param_value in engine_data.items():
        if param_name == 'engine':
            pass
        elif param_name == 'categories':
            if param_value == 'none':
                engine.categories = []
            else:
                engine.categories = list(map(str.strip, param_value.split(',')))
        elif param_name == 'proxies':
            engine.proxies = get_proxy_cycles(param_value)
        else:
            setattr(engine, param_name, param_value)

    for arg_name, arg_value in engine_default_args.items():
        if not hasattr(engine, arg_name):
            setattr(engine, arg_name, arg_value)

    # checking required variables
    for engine_attr in dir(engine):
        if engine_attr.startswith('_'):
            continue
        if engine_attr == 'inactive' and getattr(engine, engine_attr) is True:
            return None
        if getattr(engine, engine_attr) is None:
            logger.error('Missing engine config attribute: "{0}.{1}"'
                         .format(engine.name, engine_attr))
            sys.exit(1)

    # assign supported languages from json file
    if engine_data['name'] in ENGINES_LANGUAGES:
        setattr(engine, 'supported_languages', ENGINES_LANGUAGES[engine_data['name']])

    # find custom aliases for non standard language codes
    if hasattr(engine, 'supported_languages'):
        if hasattr(engine, 'language_aliases'):
            language_aliases = getattr(engine, 'language_aliases')
        else:
            language_aliases = {}

        for engine_lang in getattr(engine, 'supported_languages'):
            iso_lang = match_language(engine_lang, babel_langs, fallback=None)
            if iso_lang and iso_lang != engine_lang and not engine_lang.startswith(iso_lang) and \
               iso_lang not in getattr(engine, 'supported_languages'):
                language_aliases[iso_lang] = engine_lang

        setattr(engine, 'language_aliases', language_aliases)

    # language_support
    setattr(engine, 'language_support', len(getattr(engine, 'supported_languages', [])) > 0)

    # assign language fetching method if auxiliary method exists
    if hasattr(engine, '_fetch_supported_languages'):
        setattr(engine, 'fetch_supported_languages',
                lambda: engine._fetch_supported_languages(get(engine.supported_languages_url)))

    # tor related settings
    if settings['outgoing'].get('using_tor_proxy'):
        # use onion url if using tor.
        if hasattr(engine, 'onion_url'):
            engine.search_url = engine.onion_url + getattr(engine, 'search_path', '')
    elif 'onions' in engine.categories:
        # exclude onion engines if not using tor.
        return None

    engine.timeout += settings['outgoing'].get('extra_proxy_timeout', 0)

    for category_name in engine.categories:
        categories.setdefault(category_name, []).append(engine)

    if engine.shortcut in engine_shortcuts:
        logger.error('Engine config error: ambigious shortcut: {0}'.format(engine.shortcut))
        sys.exit(1)

    engine_shortcuts[engine.shortcut] = engine.name

    return engine


def load_engines(engine_list):
    global engines, engine_shortcuts
    engines.clear()
    engine_shortcuts.clear()
    for engine_data in engine_list:
        engine = load_engine(engine_data)
        if engine is not None:
            engines[engine.name] = engine
    return engines


def initialize_engines(engine_list):
    load_engines(engine_list)

    def engine_init(engine_name, init_fn):
        try:
            init_fn(get_engine_from_settings(engine_name))
        except Exception:
            logger.exception('%s engine: Fail to initialize', engine_name)
        else:
            logger.debug('%s engine: Initialized', engine_name)

    for engine_name, engine in engines.items():
        if hasattr(engine, 'init'):
            init_fn = getattr(engine, 'init')
            if init_fn:
                logger.debug('%s engine: Starting background initialization', engine_name)
                threading.Thread(target=engine_init, args=(engine_name, init_fn)).start()

        _set_https_support_for_engine(engine)


def _set_https_support_for_engine(engine):
    # check HTTPS support if it is not disabled
    if engine.engine_type != 'offline' and not hasattr(engine, 'https_support'):
        params = engine.request('http_test', {
            'method': 'GET',
            'headers': {},
            'data': {},
            'url': '',
            'cookies': {},
            'verify': True,
            'auth': None,
            'pageno': 1,
            'time_range': None,
            'language': '',
            'safesearch': False,
            'is_test': True,
            'category': 'files',
            'raise_for_status': True,
        })

        if 'url' not in params:
            return

        parsed_url = urlparse(params['url'])
        https_support = parsed_url.scheme == 'https'

        setattr(engine, 'https_support', https_support)
