# -*- coding: utf-8 -*-

import os
import mock
try:
    import importlib
except ImportError:
    importlib = None  # type: ignore
try:
    import pathlib
except ImportError:
    pathlib = None  # type: ignore

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from searx.testing import SearxTestCase


class EngineTest(SearxTestCase):

    maxDiff = None

    def test_response(self):
        if not(pathlib and importlib):
            return
        html_folder = 'tests/html'
        htmls = pathlib.Path(html_folder).glob('*.html')
        params = []
        for html in htmls:
            engine_name = html.name.rsplit('_', 2)[0]
            dt_parts = '_'.join(html.name.rsplit('_', 2)[1:]).split('.')[0]
            yaml_file = '{}_{}.yaml'.format(engine_name, dt_parts)

            with open(html) as f:
                html_content = f.read()

            yaml_content = None
            yaml_full_path = os.path.join(html_folder, yaml_file)
            if yaml and os.path.isfile(yaml_full_path):
                with open(yaml_full_path) as f:
                    yaml_content = yaml.load(f, Loader=yaml.FullLoader)
            params.append((html.name, engine_name, html_content, yaml_content))
        if not params:
            return

        for html_name, engine_name, html_content, yaml_content in params:
            em = importlib.import_module("searx.engines.{}".format(engine_name))
            kwargs = {}
            if em.__name__ == 'searx.engines.google':
                kwargs = dict(
                    url='http://google.com',
                    search_params={'google_hostname': 'google.com'})
            resp = mock.Mock(text=html_content, **kwargs)
            results = em.response(resp)  # type: ignore
            self.assertTrue(
                results, msg='engine:{}, file:{}'.format(engine_name, html_name))
            if yaml_content:
                self.assertEqual(results, yaml_content)
