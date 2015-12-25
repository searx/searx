
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

from os.path import realpath, dirname, splitext, join
import sys
from imp import load_source
from searx import settings
from searx import logger


logger = logger.getChild('engines')

engine_dir = dirname(realpath(__file__))

engines = {}

categories = {'general': []}

engine_shortcuts = {}


def load_module(filename):
    modname = splitext(filename)[0]
    if modname in sys.modules:
        del sys.modules[modname]
    filepath = join(engine_dir, filename)
    module = load_source(modname, filepath)
    module.name = modname
    return module


def load_engine(engine_data):
    engine_name = engine_data['engine']
    engine = load_module(engine_name + '.py')

    for param_name in engine_data:
        if param_name == 'engine':
            continue
        if param_name == 'categories':
            if engine_data['categories'] == 'none':
                engine.categories = []
            else:
                engine.categories = map(
                    str.strip, engine_data['categories'].split(','))
            continue
        setattr(engine, param_name, engine_data[param_name])

    if not hasattr(engine, 'paging'):
        engine.paging = False

    if not hasattr(engine, 'categories'):
        engine.categories = ['general']

    if not hasattr(engine, 'language_support'):
        engine.language_support = True

    if not hasattr(engine, 'safesearch'):
        engine.safesearch = False

    if not hasattr(engine, 'timeout'):
        engine.timeout = settings['outgoing']['request_timeout']

    if not hasattr(engine, 'shortcut'):
        engine.shortcut = ''

    if not hasattr(engine, 'disabled'):
        engine.disabled = False

    # checking required variables
    for engine_attr in dir(engine):
        if engine_attr.startswith('_'):
            continue
        if getattr(engine, engine_attr) is None:
            logger.error('Missing engine config attribute: "{0}.{1}"'
                         .format(engine.name, engine_attr))
            sys.exit(1)

    if hasattr(engine, 'categories'):
        for category_name in engine.categories:
            categories.setdefault(category_name, []).append(engine)
    else:
        categories['general'].append(engine)

    if engine.shortcut:
        if engine.shortcut in engine_shortcuts:
            logger.error('Engine config error: ambigious shortcut: {0}'
                         .format(engine.shortcut))
            sys.exit(1)
        engine_shortcuts[engine.shortcut] = engine.name
    return engine


if 'engines' not in settings or not settings['engines']:
    logger.error('No engines found. Edit your settings.yml')
    exit(2)

for engine_data in settings['engines']:
    engine = load_engine(engine_data)
    engines[engine.name] = engine
