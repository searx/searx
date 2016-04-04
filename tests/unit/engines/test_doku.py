# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import doku
from searx.testing import SearxTestCase


class TestDokuEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        params = doku.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, doku.response, None)
        self.assertRaises(AttributeError, doku.response, [])
        self.assertRaises(AttributeError, doku.response, '')
        self.assertRaises(AttributeError, doku.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(doku.response(response), [])

        html = u"""
        <div class="search_quickresult">
            <h3>Pages trouvées :</h3>
            <ul class="search_quickhits">
                <li> <a href="/xfconf-query" class="wikilink1" title="xfconf-query">xfconf-query</a></li>
            </ul>
            <div class="clearer"></div>
        </div>
        """
        response = mock.Mock(text=html)
        results = doku.response(response)
        expected = [{'content': '', 'title': 'xfconf-query', 'url': 'http://localhost:8090/xfconf-query'}]
        self.assertEqual(doku.response(response), expected)

        html = u"""
        <dl class="search_results">
            <dt><a href="/xvnc?s[]=query" class="wikilink1" title="xvnc">xvnc</a>: 40 Occurrences trouvées</dt>
            <dd>er = /usr/bin/Xvnc
     server_args = -inetd -<strong class="search_hit">query</strong> localhost -geometry 640x480 ... er = /usr/bin/Xvnc
     server_args = -inetd -<strong class="search_hit">query</strong> localhost -geometry 800x600 ... er = /usr/bin/Xvnc
     server_args = -inetd -<strong class="search_hit">query</strong> localhost -geometry 1024x768 ... er = /usr/bin/Xvnc
     server_args = -inetd -<strong class="search_hit">query</strong> localhost -geometry 1280x1024 -depth 8 -Sec</dd>
            <dt><a href="/postfix_mysql_tls_sasl_1404?s[]=query"
                   class="wikilink1"
                   title="postfix_mysql_tls_sasl_1404">postfix_mysql_tls_sasl_1404</a>: 14 Occurrences trouvées</dt>
            <dd>tdepasse
  hosts = 127.0.0.1
  dbname = postfix
  <strong class="search_hit">query</strong> = SELECT goto FROM alias WHERE address='%s' AND a... tdepasse
  hosts = 127.0.0.1
  dbname = postfix
  <strong class="search_hit">query</strong> = SELECT domain FROM domain WHERE domain='%s'
  #optional <strong class="search_hit">query</strong> to use when relaying for backup MX
  #<strong class="search_hit">query</strong> = SELECT domain FROM domain WHERE domain='%s' and backupmx =</dd>
          <dt><a href="/bind9?s[]=query" class="wikilink1" title="bind9">bind9</a>: 12 Occurrences trouvées</dt>
          <dd>  printcmd
;; Got answer:
;; -&gt;&gt;HEADER&lt;&lt;- opcode: <strong class="search_hit">QUERY</strong>, status: NOERROR, id: 13427
;; flags: qr aa rd ra; <strong class="search_hit">QUERY</strong>: 1, ANSWER: 1, AUTHORITY: 1, ADDITIONAL: 1

[...]

;; <strong class="search_hit">Query</strong> time: 1 msec
;; SERVER: 127.0.0.1#53(127.0.0.1)
;... par la requête (<strong class="search_hit">Query</strong> time) , entre la première et la deuxième requête.</dd>
        </dl>
        """
        response = mock.Mock(text=html)
        results = doku.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'xvnc')
# FIXME        self.assertEqual(results[0]['url'], u'http://this.should.be.the.link/ű')
# FIXME        self.assertEqual(results[0]['content'], 'This should be the content.')
