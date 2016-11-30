# -*- coding: utf-8 -*-
"""Shared testing code."""


import os
import subprocess
import traceback


from os.path import dirname, join, abspath

from splinter import Browser
from unittest2 import TestCase


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


class SearxRobotLayer():
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


# SEARXROBOTLAYER = SearxRobotLayer()
def run_robot_tests(tests):
    print('Running {0} tests'.format(len(tests)))
    for test in tests:
        with Browser() as browser:
            test(browser)


class SearxTestCase(TestCase):
    """Base test case for non-robot tests."""

    layer = SearxTestLayer


if __name__ == '__main__':
    import sys
    # test cases
    from tests import robot

    base_dir = abspath(join(dirname(__file__), '../tests'))
    if sys.argv[1] == 'robot':
        test_layer = SearxRobotLayer()
        errors = False
        try:
            test_layer.setUp()
            run_robot_tests([getattr(robot, x) for x in dir(robot) if x.startswith('test_')])
        except Exception:
            errors = True
            print('Error occured: {0}'.format(traceback.format_exc()))
        test_layer.tearDown()
        sys.exit(1 if errors else 0)
