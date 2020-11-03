#!/usr/bin/env python

# set path
from sys import path
from os.path import realpath, dirname, join
path.append(realpath(dirname(realpath(__file__)) + '/../'))

import argparse
import sys
import string
import ruamel.yaml
import secrets
import collections
from ruamel.yaml.scalarstring import SingleQuotedScalarString, DoubleQuotedScalarString
from searx.settings import load_settings, check_settings_yml, get_default_settings_path
from searx.exceptions import SearxSettingsException


RANDOM_STRING_LETTERS = string.ascii_lowercase + string.digits + string.ascii_uppercase


def get_random_string():
    r = [secrets.choice(RANDOM_STRING_LETTERS) for _ in range(64)]
    return ''.join(r)


def main(prog_arg):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=4, sequence=1, offset=2)
    user_settings_path = prog_args.get('user-settings-yaml')

    try:
        default_settings, _ = load_settings(False)
        if check_settings_yml(user_settings_path):
            with open(user_settings_path, 'r', encoding='utf-8') as f:
                user_settings = yaml.load(f.read())
            new_user_settings = False
        else:
            user_settings = yaml.load('use_default_settings: True')
            new_user_settings = True
    except SearxSettingsException as e:
        sys.stderr.write(str(e))
        return

    if not new_user_settings and not user_settings.get('use_default_settings'):
        sys.stderr.write('settings.yml already exists and use_default_settings is not True')
        return

    user_settings['use_default_settings'] = True
    use_default_settings_comment = "settings based on " + get_default_settings_path()
    user_settings.yaml_add_eol_comment(use_default_settings_comment, 'use_default_settings')

    if user_settings.get('server', {}).get('secret_key') in [None, 'ultrasecretkey']:
        user_settings.setdefault('server', {})['secret_key'] = DoubleQuotedScalarString(get_random_string())

    user_engines = user_settings.get('engines')
    if user_engines:
        has_user_engines = True
        user_engines_dict = dict((definition['name'], definition) for definition in user_engines)
    else:
        has_user_engines = False
        user_engines_dict = {}
        user_engines = []

    # remove old engines
    if prog_arg.get('add-engines') or has_user_engines:
        default_engines_dict = dict((definition['name'], definition) for definition in default_settings['engines'])
        for i, engine in enumerate(user_engines):
            if engine['name'] not in default_engines_dict:
                del user_engines[i]

    # add new engines
    if prog_arg.get('add-engines'):
        for engine in default_settings.get('engines', {}):
            if engine['name'] not in user_engines_dict:
                user_engines.append({'name': engine['name']})
        user_settings['engines'] = user_engines

    # output
    if prog_arg.get('dry-run'):
        yaml.dump(user_settings, sys.stdout)
    else:
        with open(user_settings_path, 'w', encoding='utf-8') as f:
            yaml.dump(user_settings, f)


def parse_args():
    parser = argparse.ArgumentParser(description='Update user settings.yml')
    parser.add_argument('--add-engines', dest='add-engines', default=False, action='store_true', help='Add new engines')
    parser.add_argument('--dry-run', dest='dry-run', default=False, action='store_true', help='Dry run')
    parser.add_argument('user-settings-yaml', type=str)
    return vars(parser.parse_args())


if __name__ == '__main__':
    prog_args = parse_args()
    main(prog_args)
