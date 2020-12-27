# SPDX-License-Identifier: AGPL-3.0-or-later
"""build environment used by shell scripts
"""

# set path
import sys
from os.path import realpath, dirname, join, sep
repo_root = realpath(dirname(realpath(__file__)) + sep + '..')
sys.path.insert(0, repo_root)

from searx import brand

name_val = [
    ('SEARX_URL'              , brand.SEARX_URL),
    ('GIT_URL'                , brand.GIT_URL),
    ('GIT_BRANCH'             , brand.GIT_BRANCH),
    ('ISSUE_URL'              , brand.ISSUE_URL),
    ('DOCS_URL'               , brand.DOCS_URL),
    ('PUBLIC_INSTANCES'       , brand.PUBLIC_INSTANCES),
    ('CONTACT_URL'            , brand.CONTACT_URL),
    ('WIKI_URL'               , brand.WIKI_URL),
    ('TWITTER_URL'            , brand.TWITTER_URL),
]

brand_env = 'utils' + sep + 'brand.env'

print('build %s' % brand_env)
with open(repo_root + sep + brand_env, 'w', encoding='utf-8') as f:
    for name, val in name_val:
        print("export %s='%s'" % (name, val), file=f)
