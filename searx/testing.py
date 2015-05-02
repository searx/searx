# -*- coding: utf-8 -*-
"""Shared testing code."""

from plone.testing import Layer
from unittest2 import TestCase


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
        exe = os.path.abspath(os.path.dirname(__file__) + '/../bin/py')

        # set robot settings path
        os.environ['SEARX_SETTINGS_PATH'] = os.path.abspath(
            os.path.dirname(__file__) + '/settings_robot.yml')

        # run the server
        self.server = subprocess.Popen(
            [exe, webapp],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    def tearDown(self):
        os.kill(self.server.pid, 15)
        # remove previously set environment variable
        del os.environ['SEARX_SETTINGS_PATH']


SEARXROBOTLAYER = SearxRobotLayer()


class SearxTestCase(TestCase):
    """Base test case for non-robot tests."""

    layer = SearxTestLayer
