# -*- coding: utf-8 -*-

from plone.testing import layered
from robotsuite import RobotTestSuite
from searx.testing import SEARXROBOTLAYER

import os
import unittest2 as unittest


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    tests = [
        os.path.join('robot', f) for f in
        os.listdir(robot_dir) if f.endswith('.robot') and
        f.startswith('test_')
    ]
    for test in tests:
        suite.addTests([
            layered(RobotTestSuite(test), layer=SEARXROBOTLAYER),
        ])
    return suite
