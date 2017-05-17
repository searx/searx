from collections import defaultdict
import mock
from searx.engines import archlinux
from searx.testing import SearxTestCase

domains = {
    'all': 'https://wiki.archlinux.org',
    'de': 'https://wiki.archlinux.de',
    'fr': 'https://wiki.archlinux.fr',
    'ja': 'https://wiki.archlinuxjp.org',
    'ro': 'http://wiki.archlinux.ro',
    'tr': 'http://archtr.org/wiki'
}


class TestArchLinuxEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dic = defaultdict(dict)
        dic['pageno'] = 1
        dic['language'] = 'en_US'
        params = archlinux.request(query, dic)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('wiki.archlinux.org' in params['url'])

        for lang, domain in domains.items():
            dic['language'] = lang
            params = archlinux.request(query, dic)
            self.assertTrue(domain in params['url'])

    def test_response(self):
        response = mock.Mock(text='<html></html>',
                             search_params={'language': 'en_US'})
        self.assertEqual(archlinux.response(response), [])

        html = """
        <ul class="mw-search-results">
          <li>
          <div class="mw-search-result-heading">
            <a href="/index.php/ATI" title="ATI">ATI</a>
          </div>
          <div class="searchresult">
            Lorem ipsum dolor sit amet
          </div>
          <div class="mw-search-result-data">
            30 KB (4,630 words) - 19:04, 17 March 2016</div>
          </li>
          <li>
          <div class="mw-search-result-heading">
            <a href="/index.php/Frequently_asked_questions" title="Frequently asked questions">
              Frequently asked questions
            </a>
          </div>
          <div class="searchresult">
            CPUs with AMDs instruction set "AMD64"
          </div>
          <div class="mw-search-result-data">
            17 KB (2,722 words) - 20:13, 21 March 2016
          </div>
          </li>
          <li>
          <div class="mw-search-result-heading">
            <a href="/index.php/CPU_frequency_scaling" title="CPU frequency scaling">CPU frequency scaling</a>
          </div>
          <div class="searchresult">
            ondemand for AMD and older Intel CPU
          </div>
          <div class="mw-search-result-data">
            15 KB (2,319 words) - 23:46, 16 March 2016
          </div>
          </li>
        </ul>
        """

        expected = [
            {
                'title': 'ATI',
                'url': 'https://wiki.archlinux.org/index.php/ATI'
            },
            {
                'title': 'Frequently asked questions',
                'url': 'https://wiki.archlinux.org/index.php/Frequently_asked_questions'
            },
            {
                'title': 'CPU frequency scaling',
                'url': 'https://wiki.archlinux.org/index.php/CPU_frequency_scaling'
            }
        ]

        response = mock.Mock(text=html)
        response.search_params = {
            'language': 'en_US'
        }
        results = archlinux.response(response)

        self.assertEqual(type(results), list)
        self.assertEqual(len(results), len(expected))

        i = 0
        for exp in expected:
            res = results[i]
            i += 1
            for key, value in exp.items():
                self.assertEqual(res[key], value)
