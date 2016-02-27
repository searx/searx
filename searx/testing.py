# -*- coding: utf-8 -*-
"""Shared testing code."""

from plone.testing import Layer
from unittest2 import TestCase
from os.path import dirname, join, abspath


import os
import subprocess


class SearxTestLayer:
    """Base layer for non-robot tests."""

    __name__ = u'SearxTestLayer'

    def setUp(cls):
        pass
    setUp = classmethod(setUp)

    def tearDown(cls):
        pass
    tearDown = classmethod(tearDown)

    def testSetUp(cls):
        pass
    testSetUp = classmethod(testSetUp)

    def testTearDown(cls):
        pass
    testTearDown = classmethod(testTearDown)


class SearxRobotLayer(Layer):
    """Searx Robot Test Layer"""

    def setUp(self):
        os.setpgrp()  # create new process group, become its leader

        # get program paths
        webapp = os.path.join(
            os.path.abspath(os.path.dirname(os.path.realpath(__file__))),
            'webapp.py'
        )
        exe = 'python'

        # set robot settings path
        os.environ['SEARX_SETTINGS_PATH'] = abspath(
            dirname(__file__) + '/settings_robot.yml')

        # run the server
        self.server = subprocess.Popen(
            [exe, webapp],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    def tearDown(self):
        os.kill(self.server.pid, 9)
        # remove previously set environment variable
        del os.environ['SEARX_SETTINGS_PATH']


SEARXROBOTLAYER = SearxRobotLayer()


class SearxTestCase(TestCase):
    """Base test case for non-robot tests."""

    layer = SearxTestLayer


if __name__ == '__main__':
    from tests.test_robot import test_suite
    import sys
    from zope.testrunner.runner import Runner

    base_dir = abspath(join(dirname(__file__), '../tests'))
    if sys.argv[1] == 'robot':
        r = Runner(['--color',
                    '--auto-progress',
                    '--stop-on-error',
                    '--path',
                    base_dir],
                   found_suites=[test_suite()])
        r.run()
        sys.exit(int(r.failed))
