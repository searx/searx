# -*- coding: utf-8 -*-
"""Installer for Searx package."""

from setuptools import setup
from setuptools import find_packages

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = read('README.rst')

setup(
    name='searx',
    version="0.1.2",
    description="A privacy-respecting, hackable metasearch engine",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords='meta search engine',
    author='Adam Tauber',
    author_email='asciimoo@gmail.com',
    url='https://github.com/asciimoo/searx',
    license='GNU Affero General Public License',
    packages=find_packages('.'),
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-babel',
        'grequests',
        'lxml',
        'pyyaml',
        'setuptools',
    ],
    extras_require={
        'test': [
            'coverage',
            'flake8',
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
            'static/*/*',
            'translations/*/*',
            'templates/*.html',
            'templates/result_templates/*.html',
        ],
    },

)
