# -*- coding: utf-8 -*-
"""Shared testing code."""

from plone.testing import Layer
from unittest2 import TestCase


import os
import subprocess
import sys


class SearxTestLayer:

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
        webapp = os.path.join(
            os.path.abspath(os.path.dirname(os.path.realpath(__file__))),
            'webapp.py'
        )
        exe = os.path.abspath(os.path.dirname(__file__) + '/../bin/py')
        self.server = subprocess.Popen(
            [exe, webapp, 'settings_robot'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    def tearDown(self):
        # TERM all processes in my group
        os.killpg(os.getpgid(self.server.pid), 15)


SEARXROBOTLAYER = SearxRobotLayer()


class SearxTestCase(TestCase):
    layer = SearxTestLayer
