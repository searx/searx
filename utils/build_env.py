# SPDX-License-Identifier: AGPL-3.0-or-later
"""build environment used by shell scripts
"""

# set path
import sys
from os.path import realpath, dirname, join, sep
repo_root = realpath(dirname(realpath(__file__)) + sep + '..')
sys.path.insert(0, repo_root)

from searx.settings_loader import load_settings

settings, settings_load_message = load_settings()
print(settings_load_message)

brand_env = 'utils' + sep + 'brand.env'
brand_py = 'searx' + sep + 'brand.py'

def get_val(group, name, default=''):
    return settings[group].get(name, False) or ''

name_val = [
    ('SEARX_URL'              , get_val('server', 'base_url')),
    ('GIT_URL'                , get_val('general','git_url')),
    ('GIT_BRANCH'             , get_val('general','git_branch')),
    ('ISSUE_URL'              , get_val('general','issue_url')),
    ('DOCS_URL'               , get_val('general','docs_url')),
    ('PUBLIC_INSTANCES'       , get_val('general','public_instances')),
    ('CONTACT_URL'            , get_val('general','contact_url')),
    ('WIKI_URL'               , get_val('general','wiki_url')),
    ('TWITTER_URL'            , get_val('general','twitter_url')),
]

print('build %s' % brand_env)
with open(repo_root + sep + brand_env, 'w', encoding='utf-8') as f:
    for name, val in name_val:
        print("export %s='%s'" % (name, val), file=f)

print('build %s' % brand_py)
with open(repo_root + sep + brand_py, 'w', encoding='utf-8') as f:
    for name, val in name_val:
        print("%s = '%s'" % (name, val), file=f)
