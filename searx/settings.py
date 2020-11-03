import collections.abc

import yaml
from searx.exceptions import SearxSettingsException
from os import environ
from os.path import dirname, join, abspath, isfile


searx_dir = abspath(dirname(__file__))


def check_settings_yml(file_name):
    if isfile(file_name):
        return file_name
    else:
        return None


def load_yaml(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as settings_yaml:
            settings = yaml.safe_load(settings_yaml)
            if not isinstance(settings, dict) or len(settings) == 0:
                raise SearxSettingsException('Empty file', file_name)
            return settings
    except IOError as e:
        raise SearxSettingsException(e, file_name)
    except yaml.YAMLError as e:
        raise SearxSettingsException(e, file_name)


def get_default_settings_path():
    return check_settings_yml(join(searx_dir, 'settings.yml'))


def get_user_settings_path():
    # find location of settings.yml
    if 'SEARX_SETTINGS_PATH' in environ:
        # if possible set path to settings using the
        # enviroment variable SEARX_SETTINGS_PATH
        return check_settings_yml(environ['SEARX_SETTINGS_PATH'])
    else:
        # if not, get it from searx code base or last solution from /etc/searx
        return check_settings_yml('/etc/searx/settings.yml')


def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def update_settings(default_settings, user_settings):
    for k, v in user_settings.items():
        if k == 'use_default_settings':
            continue
        elif k == 'engines':
            default_engines = default_settings[k]
            default_engines_dict = dict((definition['name'], definition) for definition in default_engines)
            default_settings[k] = [update_dict(default_engines_dict[definition['name']], definition)
                                   for definition in v]
        else:
            update_dict(default_settings[k], v)

    return default_settings


def load_settings(load_user_setttings=True):
    default_settings_path = get_default_settings_path()
    user_settings_path = get_user_settings_path()
    if user_settings_path is None or not load_user_setttings:
        # no user settings
        return (load_yaml(default_settings_path),
                'load the default settings from {}'.format(default_settings_path))

    # user settings
    user_settings = load_yaml(user_settings_path)
    if user_settings.get('use_default_settings'):
        # the user settings are merged with the default configuration
        default_settings = load_yaml(default_settings_path)
        update_settings(default_settings, user_settings)
        return (default_settings,
                'merge the default settings ( {} ) and the user setttings ( {} )'
                .format(default_settings_path, user_settings_path))

    # the user settings, fully replace the default configuration
    return (user_settings,
            'load the user settings from {}'.format(user_settings_path))
