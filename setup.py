# -*- coding: utf-8 -*-
"""Installer for Searx package."""

from setuptools import setup
from setuptools import find_packages

import os
import sys

# required to load VERSION_STRING constant
sys.path.insert(0, './searx')
from version import VERSION_STRING


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = read('README.rst')

setup(
    name='searx',
    version=VERSION_STRING,
    description="A privacy-respecting, hackable metasearch engine",
    long_description=long_description,
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
    url='https://github.com/asciimoo/searx',
    license='GNU Affero General Public License',
    packages=find_packages('.'),
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-babel',
        'requests',
        'lxml',
        'pyyaml',
        'setuptools',
        'python-dateutil',
    ],
    extras_require={
        'test': [
            'coverage',
            'flake8',
            'mock',
            'plone.testing',
            'robotframework',
            'robotframework-debuglibrary',
            'robotframework-httplibrary',
            'robotframework-selenium2library',
            'robotsuite',
            'unittest2',
            'zope.testrunner',
        ]
    },
    entry_points={
        'console_scripts': [
            'searx-run = searx.webapp:run'
        ]
    },
    package_data={
        'searx': [
            'settings.yml',
            '../README.rst',
            'static/*/*/*.*',
            'static/*/*/*/*.*',
            'static/*/*/*/*/*.*',
            'translations/*/*/*',
            'templates/*/*.*',
            'templates/*/*/*.*',
            'https_rules/*.xml'
        ],
    },

)
