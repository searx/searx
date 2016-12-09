# -*- coding: utf-8 -*-

from mock import Mock

from searx.answerers import answerers
from searx.testing import SearxTestCase


class AnswererTest(SearxTestCase):

    def test_unicode_input(self):
        query = Mock()
        unicode_payload = u'árvíztűrő tükörfúrógép'
        for answerer in answerers:
            query.query = u'{} {}'.format(answerer.keywords[0], unicode_payload)
            self.assertTrue(isinstance(answerer.answer(query), list))
