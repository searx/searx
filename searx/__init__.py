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

import logging
import searx.settings_loader
from os import environ
from os.path import realpath, dirname, join, abspath, isfile


searx_dir = abspath(dirname(__file__))
engine_dir = dirname(realpath(__file__))
static_path = abspath(join(dirname(__file__), 'static'))
settings, settings_load_message = searx.settings_loader.load_settings()

if settings['ui']['static_path']:
    static_path = settings['ui']['static_path']

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
logger.info(settings_load_message)
logger.info('Initialisation done')

if 'SEARX_SECRET' in environ:
    settings['server']['secret_key'] = environ['SEARX_SECRET']
if 'SEARX_BIND_ADDRESS' in environ:
    settings['server']['bind_address'] = environ['SEARX_BIND_ADDRESS']


class _brand_namespace:

    @classmethod
    def get_val(cls, group, name, default=''):
        return settings.get(group, {}).get(name) or default

    @property
    def SEARX_URL(self):
        return self.get_val('server', 'base_url')

    @property
    def CONTACT_URL(self):
        return self.get_val('general', 'contact_url')

    @property
    def GIT_URL(self):
        return self.get_val('brand', 'git_url')

    @property
    def GIT_BRANCH(self):
        return self.get_val('brand', 'git_branch')

    @property
    def ISSUE_URL(self):
        return self.get_val('brand', 'issue_url')

    @property
    def DOCS_URL(self):
        return self.get_val('brand', 'docs_url')

    @property
    def PUBLIC_INSTANCES(self):
        return self.get_val('brand', 'public_instances')

    @property
    def WIKI_URL(self):
        return self.get_val('brand', 'wiki_url')

    @property
    def TWITTER_URL(self):
        return self.get_val('brand', 'twitter_url')


brand = _brand_namespace()
