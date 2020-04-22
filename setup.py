# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Installer for Searx package."""

from setuptools import setup
from setuptools import find_packages

import os
import sys

# required to load VERSION_STRING constant
sys.path.insert(0, './searx')
from version import (
    VERSION_STRING,
    PLUGIN_ENTRY_POINTS
)
import brand

with open('README.rst') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = [ l.strip() for l in f.readlines()]

with open('requirements-dev.txt') as f:
    dev_requirements = [ l.strip() for l in f.readlines()]

setup(
    name='searx',
    version=VERSION_STRING,
    description="A privacy-respecting, hackable metasearch engine",
    long_description=long_description,
    url=brand.DOCS_URL,
    project_urls={
        "Code": brand.GIT_URL,
        "Issue tracker": brand.ISSUE_URL
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        'License :: OSI Approved :: GNU Affero General Public License v3'
    ],
    keywords='metasearch searchengine search web http',
    author='Adam Tauber',
    author_email='asciimoo@gmail.com',
    license='GNU Affero General Public License',
    packages=find_packages(exclude=["tests*"]),
    zip_safe=False,
    install_requires=requirements,
    extras_require={
        'test': dev_requirements
    },
    entry_points={
        'console_scripts': [
            'searx-run = searx.webapp:run'
        ],
        'searx.plugins': PLUGIN_ENTRY_POINTS,
    },
    package_data={
        'searx': [
            'settings.yml',
            '../README.rst',
            '../requirements.txt',
            '../requirements-dev.txt',
            'data/*',
            'plugins/*/*',
            'static/*.*',
            'static/*/*.*',
            'static/*/*/*.*',
            'static/*/*/*/*.*',
            'static/*/*/*/*/*.*',
            'templates/*/*.*',
            'templates/*/*/*.*',
            'tests/*',
            'tests/*/*',
            'tests/*/*/*',
            'translations/*/*/*'
        ],
    },

)
