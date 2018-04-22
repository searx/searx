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

import certifi
import logging
from os import environ
from os.path import realpath, dirname, join, abspath, isfile
from io import open as io_open
from ssl import OPENSSL_VERSION_INFO, OPENSSL_VERSION
try:
    from yaml import load
except:
    from sys import exit, stderr
    stderr.write('[E] install pyyaml\n')
    exit(2)

searx_dir = abspath(dirname(__file__))
engine_dir = dirname(realpath(__file__))


def build_key_to_index(seq, key):
    return dict((d[key], index) for (index, d) in enumerate(seq))


def file_or_none(file_name):
    if isfile(file_name):
        return file_name
    else:
        return None


def load_yaml(file_name):
    with io_open(file_name, 'r', encoding='utf-8') as file_yaml:
        return load(file_yaml)


def get_embedded_filename(name):
    return join(searx_dir, name)


def update_settings_with_path(settings, path, key=None):
    if path is None or path == '':
        return
    elif isfile(path):
        logger.debug('read configuration from %s', path)
        y = load_yaml(path)
        if isinstance(settings, dict):
            settings.update(y)
        elif isinstance(settings, list):
            kindex = build_key_to_index(settings, key)
            for e in y:
                if key is not None and key in e:
                    i = kindex.get(e[key], None)
                    if i is not None:
                        settings[i] = e
                        continue
                settings.append(e)
        else:
            logger.error('%s content is neither a list nor a dictionary')
    else:
        logger.error('%s is not a file', path)


# find location of settings.yml
if 'SEARX_SETTINGS_PATH' in environ:
    # if possible set path to settings using the
    # enviroment variable SEARX_SETTINGS_PATH
    user_settings_path = file_or_none(environ['SEARX_SETTINGS_PATH'])
else:
    # if not, get it from searx code base or last solution from /etc/searx
    user_settings_path = file_or_none(get_embedded_filename('settings.yml')) or file_or_none('/etc/searx/settings.yml')

if not user_settings_path:
    raise Exception('settings.yml not found')

user_settings = load_yaml(user_settings_path)

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
    searx_debug = user_settings.get('general', {}).get('debug')

if searx_debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger('searx')
logger.debug('read configuration from %s', user_settings_path)
# Workaround for openssl versions <1.0.2
# https://github.com/certifi/python-certifi/issues/26
if OPENSSL_VERSION_INFO[0:3] < (1, 0, 2):
    if hasattr(certifi, 'old_where'):
        environ['REQUESTS_CA_BUNDLE'] = certifi.old_where()
    logger.warning('You are using an old openssl version({0}), please upgrade above 1.0.2!'.format(OPENSSL_VERSION))

'''
Load all settings
'''
# settings are merged from different yml files
settings = {
    'search': {
        'engines': list()
    },
    'engines': list(),
    'locales': dict(),
    'doi': dict()
}
# load embedded settings first
update_settings_with_path(settings['engines'],
                          user_settings.get('search', {}).get('engines_path', None)
                          or get_embedded_filename('engines.yml'))
update_settings_with_path(settings['doi'], get_embedded_filename('doi.yml'))
update_settings_with_path(settings['locales'], get_embedded_filename('locales.yml'))
# load user settings (may override embedded settings)
settings.update(user_settings)
# add additional engines (replace engine definition if it already exists)
update_settings_with_path(settings['engines'],
                          user_settings.get('search', {}).get('include_engines_path', None), 'name')
# are there some user engine settings ?
user_engine_settings = settings.get('search', {}).get('engines', None)
if user_engine_settings:
    # Yes there are, so disable all engines by default
    for e in settings['engines']:
        e['disabled'] = True

    # merge settings "search.engines" into "engines"
    engines_by_names = build_key_to_index(settings['engines'], 'name')
    for e in user_engine_settings:
        name = e['name']
        del e['name']
        # enable engine
        e['disabled'] = False
        # merge settings
        if name in engines_by_names:
            settings['engines'][engines_by_names[name]].update(e)
        else:
            logger.error('{0} is not an engine')

    # merge done : delete user engine settings
    del settings['search']['engines']

#
logger.info('Initialisation done')

if 'SEARX_SECRET' in environ:
    settings['server']['secret_key'] = environ['SEARX_SECRET']
