import logging
import os
from os import environ
from os.path import realpath, dirname, join, abspath, isfile
from io import open
from yaml import safe_load


def check_settings_yml(file_name):
    if isfile(file_name):
        return file_name
    else:
        return None


def load_settings():
    # find location of settings.yml
    if 'SEARX_SETTINGS_PATH' in environ:
        # if possible set path to settings using the
        # enviroment variable SEARX_SETTINGS_PATH
        settings_path = check_settings_yml(environ['SEARX_SETTINGS_PATH'])
    else:
        # if not, get it from searx code base or last solution from /etc/searx
        settings_path = check_settings_yml(join(searx_dir, 'settings.yml'))\
            or check_settings_yml('/etc/searx/settings.yml')

    if not settings_path:
        raise Exception('settings.yml not found')

    # load settings
    with open(settings_path, 'r', encoding='utf-8') as settings_yaml:
        return safe_load(settings_yaml)
    logger = logging.getLogger('searx')
    logger.debug('read configuration from %s', settings_path)


def set_debug_mode(settings):
    '''
    enable debug if
    the environnement variable SEARX_DEBUG is 1 or true
    (whatever the value in settings.yml)
    or general.debug=True in settings.yml

    disable debug if
    the environnement variable SEARX_DEBUG is 0 or false
    (whatever the value in settings.yml)
    or general.debug=False in settings.yml
    '''
    searx_debug_env = environ.get('SEARX_DEBUG', '').lower()
    if searx_debug_env == 'true' or searx_debug_env == '1':
        searx_debug = True
    elif searx_debug_env == 'false' or searx_debug_env == '0':
        searx_debug = False
    else:
        searx_debug = settings.get('general', {}).get('debug')

    if searx_debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    return searx_debug


def get_resources_directory(searx_directory, subdirectory, resources_directory):
    if not resources_directory:
        resources_directory = os.path.join(searx_directory, subdirectory)
    if not os.path.isdir(resources_directory):
        raise Exception(resources_directory + " is not a directory")
    return resources_directory


def get_static_files(static_path):
    static_files = set()
    static_path_length = len(static_path) + 1
    for directory, _, files in os.walk(static_path):
        for filename in files:
            f = os.path.join(directory[static_path_length:], filename)
            static_files.add(f)
    return static_files


def get_result_templates(templates_path):
    result_templates = set()
    templates_path_length = len(templates_path) + 1
    for directory, _, files in os.walk(templates_path):
        if directory.endswith('result_templates'):
            for filename in files:
                f = os.path.join(directory[templates_path_length:], filename)
                result_templates.add(f)
    return result_templates


def get_themes(templates_path):
    """Returns available themes list."""
    themes = os.listdir(templates_path)
    if '__common__' in themes:
        themes.remove('__common__')
    return themes


#
searx_dir = abspath(dirname(__file__))

#
settings = load_settings()
searx_debug = set_debug_mode(settings)
logger = logging.getLogger('searx')

if searx_debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

#
if 'SEARX_SECRET' in environ:
    settings['server']['secret_key'] = environ['SEARX_SECRET']
if 'SEARX_BIND_ADDRESS' in environ:
    settings['server']['bind_address'] = environ['SEARX_BIND_ADDRESS']
if not searx_debug and settings['server']['secret_key'] == 'ultrasecretkey':
    logger.error('server.secret_key is not changed. Please use something else instead of ultrasecretkey.')
    exit(1)

# themes
default_theme = settings['ui']['default_theme']
templates_path = get_resources_directory(searx_dir, 'templates', settings['ui']['templates_path'])
themes = get_themes(templates_path)
result_templates = get_result_templates(templates_path)
logger.debug('templates directory is %s', templates_path)

# static
static_path = get_resources_directory(searx_dir, 'static', settings['ui']['static_path'])
static_files = get_static_files(static_path)
logger.debug('static directory is %s', static_path)

# global_favicons
global_favicons = []
for indice, theme in enumerate(themes):
    global_favicons.append([])
    theme_img_path = os.path.join(static_path, 'themes', theme, 'img', 'icons')
    for (dirpath, dirnames, filenames) in os.walk(theme_img_path):
        global_favicons[indice].extend(filenames)
