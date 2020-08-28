# -*- coding: utf-8 -*-

import unittest2 as unittest
from unittest2.util import strclass
from searx.engines import load_engine
from searx import settings


class TestEngine(unittest.TestCase):

    def test_engines(self):
        for engine_data in settings['engines']:
            load_engine(engine_data)
