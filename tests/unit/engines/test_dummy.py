from searx.engines import dummy
from searx.testing import SearxTestCase


class TestDummyEngine(SearxTestCase):

    def test_request(self):
        test_params = [
            [1, 2, 3],
            ['a'],
            [],
            1
        ]
        for params in test_params:
            self.assertEqual(dummy.request(None, params), params)

    def test_response(self):
        responses = [
            None,
            [],
            True,
            dict(),
            tuple()
        ]
        for response in responses:
            self.assertEqual(dummy.response(response), [])
