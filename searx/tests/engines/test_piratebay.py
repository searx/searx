# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import piratebay
from searx.testing import SearxTestCase


class TestPiratebayEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['category'] = 'Toto'
        params = piratebay.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('piratebay.se', params['url'])
        self.assertIn('0', params['url'])

        dicto['category'] = 'music'
        params = piratebay.request(query, dicto)
        self.assertIn('100', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, piratebay.response, None)
        self.assertRaises(AttributeError, piratebay.response, [])
        self.assertRaises(AttributeError, piratebay.response, '')
        self.assertRaises(AttributeError, piratebay.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(piratebay.response(response), [])

        html = """
        <table id="searchResult">
            <tr>
            </tr>
            <tr>
                <td class="vertTh">
                    <center>
                        <a href="#" title="More from this category">Anime</a><br/>
                        (<a href="#" title="More from this category">Anime</a>)
                    </center>
                </td>
                <td>
                    <div class="detName">
                        <a href="/this.is.the.link" class="detLink" title="Title">
                            This is the title
                        </a>
                    </div>
                    <a href="magnet:?xt=urn:btih:MAGNETLINK" title="Download this torrent using magnet">
                        <img src="/static/img/icon-magnet.gif" alt="Magnet link"/>
                    </a>
                    <a href="http://torcache.net/torrent/TORRENTFILE.torrent" title="Download this torrent">
                        <img src="/static/img/dl.gif" class="dl" alt="Download"/>
                    </a>
                    <a href="/user/HorribleSubs">
                        <img src="/static/img/vip.gif" alt="VIP" title="VIP" style="width:11px;" border='0'/>
                    </a>
                    <img src="/static/img/11x11p.png"/>
                    <font class="detDesc">
                        This is the content <span>and should be</span> OK
                    </font>
                </td>
                <td align="right">13</td>
                <td align="right">334</td>
            </tr>
            <tr>
                <td class="vertTh">
                    <center>
                        <a href="#" title="More from this category">Anime</a><br/>
                        (<a href="#" title="More from this category">Anime</a>)
                    </center>
                </td>
                <td>
                    <div class="detName">
                        <a href="/this.is.the.link" class="detLink" title="Title">
                            This is the title
                        </a>
                    </div>
                    <a href="magnet:?xt=urn:btih:MAGNETLINK" title="Download this torrent using magnet">
                        <img src="/static/img/icon-magnet.gif" alt="Magnet link"/>
                    </a>
                    <a href="/user/HorribleSubs">
                        <img src="/static/img/vip.gif" alt="VIP" title="VIP" style="width:11px;" border='0'/>
                    </a>
                    <img src="/static/img/11x11p.png"/>
                    <font class="detDesc">
                        This is the content <span>and should be</span> OK
                    </font>
                </td>
                <td align="right">13</td>
                <td align="right">334</td>
            </tr>
        </table>
        """
        response = mock.Mock(text=html)
        results = piratebay.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://thepiratebay.se/this.is.the.link')
        self.assertEqual(results[0]['content'], 'This is the content and should be OK')
        self.assertEqual(results[0]['seed'], 13)
        self.assertEqual(results[0]['leech'], 334)
        self.assertEqual(results[0]['magnetlink'], 'magnet:?xt=urn:btih:MAGNETLINK')
        self.assertEqual(results[0]['torrentfile'], 'http://torcache.net/torrent/TORRENTFILE.torrent')

        self.assertEqual(results[1]['torrentfile'], None)

        html = """
        <table id="searchResult">
            <tr>
            </tr>
            <tr>
                <td class="vertTh">
                    <center>
                        <a href="#" title="More from this category">Anime</a><br/>
                        (<a href="#" title="More from this category">Anime</a>)
                    </center>
                </td>
                <td>
                    <div class="detName">
                        <a href="/this.is.the.link" class="detLink" title="Title">
                            This is the title
                        </a>
                    </div>
                    <a href="magnet:?xt=urn:btih:MAGNETLINK" title="Download this torrent using magnet">
                        <img src="/static/img/icon-magnet.gif" alt="Magnet link"/>
                    </a>
                    <a href="http://torcache.net/torrent/TORRENTFILE.torrent" title="Download this torrent">
                        <img src="/static/img/dl.gif" class="dl" alt="Download"/>
                    </a>
                    <a href="/user/HorribleSubs">
                        <img src="/static/img/vip.gif" alt="VIP" title="VIP" style="width:11px;" border='0'/>
                    </a>
                    <img src="/static/img/11x11p.png"/>
                    <font class="detDesc">
                        This is the content <span>and should be</span> OK
                    </font>
                </td>
                <td align="right">s</td>
                <td align="right">d</td>
            </tr>
        </table>
        """
        response = mock.Mock(text=html)
        results = piratebay.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://thepiratebay.se/this.is.the.link')
        self.assertEqual(results[0]['content'], 'This is the content and should be OK')
        self.assertEqual(results[0]['seed'], 0)
        self.assertEqual(results[0]['leech'], 0)
        self.assertEqual(results[0]['magnetlink'], 'magnet:?xt=urn:btih:MAGNETLINK')
        self.assertEqual(results[0]['torrentfile'], 'http://torcache.net/torrent/TORRENTFILE.torrent')

        html = """
        <table id="searchResult">
        </table>
        """
        response = mock.Mock(text=html)
        results = piratebay.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
