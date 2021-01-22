# SPDX-License-Identifier: AGPL-3.0-or-later
import os
import sys
import requests
import logging
from os.path import dirname, abspath

searx_dir = abspath(dirname(__file__))

logger = logging.getLogger('searx')


def default(value):
    def f(existing, path):
        if not existing:
            return value
        return value
    return f


def is_instance(types):
    def f(existing, path):
        nonlocal types
        if None in types and existing is None:
            return existing
        else:
            types = tuple(filter(lambda t: t is not None, types))
        if not isinstance(existing, types):
            types_str = list(map(lambda t: t.__name__ if t is not None else 'None', types))
            logger.critical('%s has to be one of these types: %s', '.'.join(path), ', '.join(types_str))
            sys.exit(1)
        return existing
    return f


def override_by_environ(environ_name):
    def f(existing, path):
        if environ_name in os.environ:
            return os.environ[environ_name]
        return existing
    return f


def override_by_bool_envriron(environ_name):
    def f(existing, path):
        if environ_name in os.environ:
            v = os.environ[environ_name].lower()
            if v == 'true' or v == '1':
                return True
            elif v == 'false' or v == '0':
                return False
            else:
                logger.warning('%s : ignore value from %s environment variable', '.'.join(path), environ_name)
        return existing
    return f


def get_resources_directory(searx_directory, subdirectory):
    resources_directory = os.path.join(searx_directory, subdirectory)
    if not os.path.isdir(resources_directory):
        raise Exception(resources_directory + " is not a directory")
    return resources_directory


def apply_schema(settings, schema, path):
    for key, value in schema.items():
        if isinstance(value, dict):
            apply_schema(settings.setdefault(key, {}), schema[key], [*path, key])
        else:
            if callable(value):
                value = (value,)
            if isinstance(value, tuple):
                for f in value:
                    if callable(f):
                        settings[key] = f(settings.get(key), [*path, key])
                    else:
                        raise Exception()
            else:
                settings.setdefault(key, value)


def settings_set_defaults(settings):
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
    schema = {
        'general': {
            'debug': (default(False), override_by_bool_envriron('SEARX_DEBUG'))
        },
        'brand': {

        },
        'search': {

        },
        'server': {
            'secret_key': override_by_environ('SEARX_SECRET'),
            'bind_address': override_by_environ('SEARX_BIND_ADDRESS'),
            'default_http_headers': default({})
        },
        'ui': {
            'templates_path': default(get_resources_directory(searx_dir, 'templates')),
            'static_path': default(get_resources_directory(searx_dir, 'static'))
        },
        'outgoing': {
            'max_request_timeout': is_instance((None, float)),
            'pool_connections': default(100),
            'pool_maxsize': default(requests.adapters.DEFAULT_POOLSIZE)
        },
        'checker': {
            'off_when_debug': default(True)
        },
        'engines': {

        },
        'doi_resolvers': {

        }
    }

    apply_schema(settings, schema, [])

    max_request_timeout = settings['outgoing']['max_request_timeout']
    if max_request_timeout is None:
        logger.info('max_request_timeout=%s', repr(max_request_timeout))
    else:
        logger.info('max_request_timeout=%i second(s)', max_request_timeout)

    return settings
