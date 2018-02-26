# -*- coding: utf-8 -*-

from mock import Mock, call

from searx.answerers import Answerers, file_loader
from searx.testing import SearxTestCase


class Query:
    query = 'test query'


class Answerer:
    keywords = ('test')

    def answer(query):
        return [{'answer': query}]

    def self_info():
        return {
            'name': 'test_answerer',
            'description': 'test_answerer',
            'examples': ['test']}


class AnswererTest(SearxTestCase):

    def test_loader_is_used(self):
        mock_loader = Mock(return_value=[Answerer()])
        answerer = Answerers(mock_loader)
        calls = []

        answerer.get()
        calls.append(call())
        mock_loader.assert_has_calls(calls, any_order=True)

        answerer.get_by_keywords()
        calls.append(call())
        mock_loader.assert_has_calls(calls, any_order=True)

        answerer.ask(Query())
        calls.append(call())
        mock_loader.assert_has_calls(calls, any_order=True)

    def test_unicode_input(self):
        query = Mock()
        unicode_payload = u'árvíztűrő tükörfúrógép'
        for answerer in Answerers(file_loader).get():
            query.query = u'{} {}'.format(answerer.keywords[0], unicode_payload)
            self.assertTrue(isinstance(answerer.answer(query), list))
