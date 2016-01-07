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
from os.path import realpath, dirname, join, abspath
from ssl import OPENSSL_VERSION_INFO, OPENSSL_VERSION
try:
    from yaml import load
except:
    from sys import exit, stderr
    stderr.write('[E] install pyyaml\n')
    exit(2)

searx_dir = abspath(dirname(__file__))
engine_dir = dirname(realpath(__file__))

# if possible set path to settings using the
# enviroment variable SEARX_SETTINGS_PATH
if 'SEARX_SETTINGS_PATH' in environ:
    settings_path = environ['SEARX_SETTINGS_PATH']
# otherwise using default path
else:
    settings_path = join(searx_dir, 'settings.yml')

# load settings
with open(settings_path) as settings_yaml:
    settings = load(settings_yaml)

if settings.get('general', {}).get('debug'):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger('searx')

# Workaround for openssl versions <1.0.2
# https://github.com/certifi/python-certifi/issues/26
if OPENSSL_VERSION_INFO[0:3] < (1, 0, 2):
    if hasattr(certifi, 'old_where'):
        environ['REQUESTS_CA_BUNDLE'] = certifi.old_where()
    logger.warning('You are using an old openssl version({0}), please upgrade above 1.0.2!'.format(OPENSSL_VERSION))

logger.info('Initialisation done')
