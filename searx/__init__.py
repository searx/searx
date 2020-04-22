# SPDX-License-Identifier: AGPL-3.0-or-later

import certifi
import logging
from os import environ
from os.path import realpath, dirname, join, abspath, isfile
from io import open
from ssl import OPENSSL_VERSION_INFO, OPENSSL_VERSION
from yaml import safe_load


def check_settings_yml(file_name):
    if isfile(file_name):
        return file_name
    else:
        return None

# find location of settings.yml
if 'SEARX_SETTINGS_PATH' in environ:
    # if possible set path to settings using the
    # enviroment variable SEARX_SETTINGS_PATH
    settings_path = check_settings_yml(environ['SEARX_SETTINGS_PATH'])
else:
    # if not, get it from searx code base or last solution from /etc/searx
    _yml = join(abspath(dirname(__file__)), 'settings.yml')
    settings_path = check_settings_yml(_yml) or check_settings_yml('/etc/searx/settings.yml')

if not settings_path:
    raise Exception('settings.yml not found')

# load settings
with open(settings_path, 'r', encoding='utf-8') as settings_yaml:
    settings = safe_load(settings_yaml)

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

logger = logging.getLogger('searx')
logger.debug('read configuration from %s', settings_path)
# Workaround for openssl versions <1.0.2
# https://github.com/certifi/python-certifi/issues/26
if OPENSSL_VERSION_INFO[0:3] < (1, 0, 2):
    if hasattr(certifi, 'old_where'):
        environ['REQUESTS_CA_BUNDLE'] = certifi.old_where()
    logger.warning('You are using an old openssl version({0}), please upgrade above 1.0.2!'.format(OPENSSL_VERSION))

logger.info('Initialisation done')

if 'SEARX_SECRET' in environ:
    settings['server']['secret_key'] = environ['SEARX_SECRET']
if 'SEARX_BIND_ADDRESS' in environ:
    settings['server']['bind_address'] = environ['SEARX_BIND_ADDRESS']
