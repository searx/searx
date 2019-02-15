# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import btdigg
from searx.testing import SearxTestCase


class TestBtdiggEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = btdigg.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('btdig.com', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, btdigg.response, None)
        self.assertRaises(AttributeError, btdigg.response, [])
        self.assertRaises(AttributeError, btdigg.response, '')
        self.assertRaises(AttributeError, btdigg.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(btdigg.response(response), [])

        html = u"""
        <div class="one_result" style="display:table-row;background-color:#e8e8e8">
          <div style="display:table-cell;color:rgb(0, 0, 0)">
            <div style="display:table">
              <div style="display:table-row">
                <div class="torrent_name" style="display:table-cell">
                  <a style="color:rgb(0, 0, 204);text-decoration:underline;font-size:150%"
                    href="http://btdig.com/a72f35b7ee3a10928f02bb799e40ae5db701ed1c/pdf?q=pdf&amp;p=1&amp;order=0"
                    >3.9GBdeLibrosByHuasoFromHell(3de4)</a>
                </div>
              </div>
            </div>
            <div style="display:table">
              <div style="display:table-row">
                <div style="display:table-cell">
                  <span class="torrent_files" style="color:#666;padding-left:10px">4217</span> files <span
                    class="torrent_size" style="color:#666;padding-left:10px">1 GB</span><span
                    class="torrent_age" style="color:rgb(0, 102, 0);padding-left:10px;margin: 0px 4px"
                    >found 3 years ago</span>
                </div>
              </div>
            </div>
            <div style="display:table;width:100%;padding:10px">
              <div style="display:table-row">
                <div class="torrent_magnet" style="display:table-cell">
                  <div class="fa fa-magnet" style="color:#cc0000">
                    <a href="magnet:?xt=urn:btih:a72f35b7ee3a10928f02bb799e40ae5db701ed1c&amp;dn=3.9GBdeLibrosBy..."
                       title="Download via magnet-link"> magnet:?xt=urn:btih:a72f35b7ee...</a>
                  </div>
                </div>
                <div style="display:table-cell;color:rgb(0, 0, 0);text-align:right">
                  <span style="color:rgb(136, 136, 136);margin: 0px 0px 0px 4px"></span><span
                    style="color:rgb(0, 102, 0);margin: 0px 4px">found 3 years ago</span>
                </div>
              </div>
            </div>
            <div class="torrent_excerpt" style="display:table;padding:10px;white-space:nowrap">
              <div class="fa fa-folder-open" style="padding-left:0em"> 3.9GBdeLibrosByHuasoFromHell(3de4)</div><br/>
              <div class="fa fa-folder-open" style="padding-left:1em"> Libros H-Z</div><br/>
              <div class="fa fa-folder-open" style="padding-left:2em"> H</div><br/><div class="fa fa-file-archive-o"
                style="padding-left:3em"> H.H. Hollis - El truco de la espada-<b
                style="color:red; background-color:yellow">pdf</b>.zip</div><span
                style="color:#666;padding-left:10px">17 KB</span><br/>
              <div class="fa fa-file-archive-o" style="padding-left:3em"> Hagakure - El Libro del Samurai-<b
                style="color:red; background-color:yellow">pdf</b>.zip</div><span
                style="color:#666;padding-left:10px">95 KB</span><br/>
              <div class="fa fa-folder-open" style="padding-left:3em"> Hamsun, Knut (1859-1952)</div><br/>
              <div class="fa fa-file-archive-o" style="padding-left:4em"> Hamsun, Knut - Hambre-<b
                style="color:red; background-color:yellow">pdf</b>.zip</div><span
                style="color:#666;padding-left:10px">786 KB</span><br/>
              <div class="fa fa-plus-circle"><a
                href="http://btdig.com/a72f35b7ee3a10928f02bb799e40ae5db701ed1c/pdf?q=pdf&amp;p=1&amp;order=0"
                > 4214 hidden files<span style="color:#666;padding-left:10px">1 GB</span></a></div>
            </div>
          </div>
        </div>
        """
        response = mock.Mock(text=html.encode('utf-8'))
        results = btdigg.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], '3.9GBdeLibrosByHuasoFromHell(3de4)')
        self.assertEqual(results[0]['url'],
                         'http://btdig.com/a72f35b7ee3a10928f02bb799e40ae5db701ed1c/pdf?q=pdf&p=1&order=0')
        self.assertEqual(results[0]['content'],
                         '3.9GBdeLibrosByHuasoFromHell(3de4) | ' +
                         'Libros H-Z | ' +
                         'H H.H. Hollis - El truco de la espada-pdf.zip17 KB | ' +
                         'Hagakure - El Libro del Samurai-pdf.zip95 KB | ' +
                         'Hamsun, Knut (1859-1952) | Hamsun, Knut - Hambre-pdf.zip786 KB | ' +
                         '4214 hidden files1 GB')
        self.assertEqual(results[0]['filesize'], 1 * 1024 * 1024 * 1024)
        self.assertEqual(results[0]['files'], 4217)
        self.assertEqual(results[0]['magnetlink'],
                         'magnet:?xt=urn:btih:a72f35b7ee3a10928f02bb799e40ae5db701ed1c&dn=3.9GBdeLibrosBy...')

        html = """
        <div style="display:table-row;background-color:#e8e8e8">

        </div>
        """
        response = mock.Mock(text=html.encode('utf-8'))
        results = btdigg.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
