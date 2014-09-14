from os import environ
from os.path import realpath, dirname, join, abspath
from searx.https_rewrite import load_https_rules
try:
    from yaml import load
except:
    from sys import exit, stderr
    stderr.write('[E] install pyyaml\n')
    exit(2)

searx_dir = abspath(dirname(__file__))
engine_dir = dirname(realpath(__file__))

if 'SEARX_SETTINGS_PATH' in environ:
    settings_path = environ['SEARX_SETTINGS_PATH']
else:
    settings_path = join(searx_dir, 'settings.yml')

if 'SEARX_HTTPS_REWRITE_PATH' in environ:
    https_rewrite_path = environ['SEARX_HTTPS_REWRITE_PATH']
else:
    https_rewrite_path = join(searx_dir, 'https_rules')

with open(settings_path) as settings_yaml:
    settings = load(settings_yaml)

# loade https rules
load_https_rules(https_rewrite_path)
