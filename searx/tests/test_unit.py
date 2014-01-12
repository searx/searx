# -*- coding: utf-8 -*-

from searx.testing import SearxTestCase


class UnitTestCase(SearxTestCase):

    def test_flask(self):
        import flask
        self.assertIn('Flask', dir(flask))
