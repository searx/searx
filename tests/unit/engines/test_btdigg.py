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
        self.assertIn('btdigg.org', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, btdigg.response, None)
        self.assertRaises(AttributeError, btdigg.response, [])
        self.assertRaises(AttributeError, btdigg.response, '')
        self.assertRaises(AttributeError, btdigg.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(btdigg.response(response), [])

        html = u"""
        <div id="search_res">
            <table>
                <tr>
                    <td class="idx">1</td>
                    <td>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="torrent_name">
                                    <a href="/url">Should be the title</a>
                                </td>
                            </tr>
                        </table>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="ttth">
                                    <a onclick="fclck(this.href)" href="magnet:?xt=urn:btih:magnet&amp;dn=Test"
                                    title="Télécharger des liens Magnet">[magnet]</a>
                                </td>
                                <td class="ttth">
                                    <a href="https://btcloud.io/manager?cmd=add&amp;info_hash=hash"
                                    target="_blank" title="Ajouter à BTCloud">[cloud]</a>
                                </td>
                                <td>
                                    <span class="attr_name">Taille:</span>
                                    <span class="attr_val">8 B</span>
                                </td>
                                <td>
                                    <span class="attr_name">Fichiers:</span>
                                    <span class="attr_val">710</span>
                                </td>
                                <td>
                                    <span class="attr_name">Téléchargements:</span>
                                    <span class="attr_val">5</span>
                                </td>
                                <td>
                                    <span class="attr_name">Temps:</span>
                                    <span class="attr_val">417.8&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Dernière&nbsp;mise&nbsp;à&nbsp;jour:</span>
                                    <span class="attr_val">5.3&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Faux:</span>
                                    <span class="attr_val">Aucun</span>
                                </td>
                            </tr>
                        </table>
                        <pre class="snippet">
                            Content
                        </pre>
                    </td>
                </tr>
            </table>
        </div>
        """
        response = mock.Mock(text=html.encode('utf-8'))
        results = btdigg.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Should be the title')
        self.assertEqual(results[0]['url'], 'https://btdigg.org/url')
        self.assertEqual(results[0]['content'], 'Content')
        self.assertEqual(results[0]['seed'], 5)
        self.assertEqual(results[0]['leech'], 0)
        self.assertEqual(results[0]['filesize'], 8)
        self.assertEqual(results[0]['files'], 710)
        self.assertEqual(results[0]['magnetlink'], 'magnet:?xt=urn:btih:magnet&dn=Test')

        html = """
        <div id="search_res">
            <table>
            </table>
        </div>
        """
        response = mock.Mock(text=html.encode('utf-8'))
        results = btdigg.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        html = u"""
        <div id="search_res">
            <table>
                <tr>
                    <td class="idx">1</td>
                    <td>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="torrent_name">
                                    <a href="/url">Should be the title</a>
                                </td>
                            </tr>
                        </table>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="ttth">
                                    <a onclick="fclck(this.href)" href="magnet:?xt=urn:btih:magnet&amp;dn=Test"
                                    title="Télécharger des liens Magnet">[magnet]</a>
                                </td>
                                <td class="ttth">
                                    <a href="https://btcloud.io/manager?cmd=add&amp;info_hash=hash"
                                    target="_blank" title="Ajouter à BTCloud">[cloud]</a>
                                </td>
                                <td>
                                    <span class="attr_name">Taille:</span>
                                    <span class="attr_val">1 KB</span>
                                </td>
                                <td>
                                    <span class="attr_name">Fichiers:</span>
                                    <span class="attr_val">710</span>
                                </td>
                                <td>
                                    <span class="attr_name">Téléchargements:</span>
                                    <span class="attr_val">5</span>
                                </td>
                                <td>
                                    <span class="attr_name">Temps:</span>
                                    <span class="attr_val">417.8&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Dernière&nbsp;mise&nbsp;à&nbsp;jour:</span>
                                    <span class="attr_val">5.3&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Faux:</span>
                                    <span class="attr_val">Aucun</span>
                                </td>
                            </tr>
                        </table>
                        <pre class="snippet">
                            Content
                        </pre>
                    </td>
                </tr>
                <tr>
                    <td class="idx">1</td>
                    <td>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="torrent_name">
                                    <a href="/url">Should be the title</a>
                                </td>
                            </tr>
                        </table>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="ttth">
                                    <a onclick="fclck(this.href)" href="magnet:?xt=urn:btih:magnet&amp;dn=Test"
                                    title="Télécharger des liens Magnet">[magnet]</a>
                                </td>
                                <td class="ttth">
                                    <a href="https://btcloud.io/manager?cmd=add&amp;info_hash=hash"
                                    target="_blank" title="Ajouter à BTCloud">[cloud]</a>
                                </td>
                                <td>
                                    <span class="attr_name">Taille:</span>
                                    <span class="attr_val">1 MB</span>
                                </td>
                                <td>
                                    <span class="attr_name">Fichiers:</span>
                                    <span class="attr_val">a</span>
                                </td>
                                <td>
                                    <span class="attr_name">Téléchargements:</span>
                                    <span class="attr_val">4</span>
                                </td>
                                <td>
                                    <span class="attr_name">Temps:</span>
                                    <span class="attr_val">417.8&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Dernière&nbsp;mise&nbsp;à&nbsp;jour:</span>
                                    <span class="attr_val">5.3&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Faux:</span>
                                    <span class="attr_val">Aucun</span>
                                </td>
                            </tr>
                        </table>
                        <pre class="snippet">
                            Content
                        </pre>
                    </td>
                </tr>
                <tr>
                    <td class="idx">1</td>
                    <td>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="torrent_name">
                                    <a href="/url">Should be the title</a>
                                </td>
                            </tr>
                        </table>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="ttth">
                                    <a onclick="fclck(this.href)" href="magnet:?xt=urn:btih:magnet&amp;dn=Test"
                                    title="Télécharger des liens Magnet">[magnet]</a>
                                </td>
                                <td class="ttth">
                                    <a href="https://btcloud.io/manager?cmd=add&amp;info_hash=hash"
                                    target="_blank" title="Ajouter à BTCloud">[cloud]</a>
                                </td>
                                <td>
                                    <span class="attr_name">Taille:</span>
                                    <span class="attr_val">1 GB</span>
                                </td>
                                <td>
                                    <span class="attr_name">Fichiers:</span>
                                    <span class="attr_val">710</span>
                                </td>
                                <td>
                                    <span class="attr_name">Téléchargements:</span>
                                    <span class="attr_val">3</span>
                                </td>
                                <td>
                                    <span class="attr_name">Temps:</span>
                                    <span class="attr_val">417.8&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Dernière&nbsp;mise&nbsp;à&nbsp;jour:</span>
                                    <span class="attr_val">5.3&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Faux:</span>
                                    <span class="attr_val">Aucun</span>
                                </td>
                            </tr>
                        </table>
                        <pre class="snippet">
                            Content
                        </pre>
                    </td>
                </tr>
                <tr>
                    <td class="idx">1</td>
                    <td>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="torrent_name">
                                    <a href="/url">Should be the title</a>
                                </td>
                            </tr>
                        </table>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="ttth">
                                    <a onclick="fclck(this.href)" href="magnet:?xt=urn:btih:magnet&amp;dn=Test"
                                    title="Télécharger des liens Magnet">[magnet]</a>
                                </td>
                                <td class="ttth">
                                    <a href="https://btcloud.io/manager?cmd=add&amp;info_hash=hash"
                                    target="_blank" title="Ajouter à BTCloud">[cloud]</a>
                                </td>
                                <td>
                                    <span class="attr_name">Taille:</span>
                                    <span class="attr_val">1 TB</span>
                                </td>
                                <td>
                                    <span class="attr_name">Fichiers:</span>
                                    <span class="attr_val">710</span>
                                </td>
                                <td>
                                    <span class="attr_name">Téléchargements:</span>
                                    <span class="attr_val">2</span>
                                </td>
                                <td>
                                    <span class="attr_name">Temps:</span>
                                    <span class="attr_val">417.8&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Dernière&nbsp;mise&nbsp;à&nbsp;jour:</span>
                                    <span class="attr_val">5.3&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Faux:</span>
                                    <span class="attr_val">Aucun</span>
                                </td>
                            </tr>
                        </table>
                        <pre class="snippet">
                            Content
                        </pre>
                    </td>
                </tr>
                <tr>
                    <td class="idx">1</td>
                    <td>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="torrent_name">
                                    <a href="/url">Should be the title</a>
                                </td>
                            </tr>
                        </table>
                        <table class="torrent_name_tbl">
                            <tr>
                                <td class="ttth">
                                    <a onclick="fclck(this.href)" href="magnet:?xt=urn:btih:magnet&amp;dn=Test"
                                    title="Télécharger des liens Magnet">[magnet]</a>
                                </td>
                                <td class="ttth">
                                    <a href="https://btcloud.io/manager?cmd=add&amp;info_hash=hash"
                                    target="_blank" title="Ajouter à BTCloud">[cloud]</a>
                                </td>
                                <td>
                                    <span class="attr_name">Taille:</span>
                                    <span class="attr_val">a TB</span>
                                </td>
                                <td>
                                    <span class="attr_name">Fichiers:</span>
                                    <span class="attr_val">710</span>
                                </td>
                                <td>
                                    <span class="attr_name">Téléchargements:</span>
                                    <span class="attr_val">z</span>
                                </td>
                                <td>
                                    <span class="attr_name">Temps:</span>
                                    <span class="attr_val">417.8&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Dernière&nbsp;mise&nbsp;à&nbsp;jour:</span>
                                    <span class="attr_val">5.3&nbsp;jours</span>
                                </td>
                                <td>
                                    <span class="attr_name">Faux:</span>
                                    <span class="attr_val">Aucun</span>
                                </td>
                            </tr>
                        </table>
                        <pre class="snippet">
                            Content
                        </pre>
                    </td>
                </tr>
            </table>
        </div>
        """
        response = mock.Mock(text=html.encode('utf-8'))
        results = btdigg.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0]['title'], 'Should be the title')
        self.assertEqual(results[0]['url'], 'https://btdigg.org/url')
        self.assertEqual(results[0]['content'], 'Content')
        self.assertEqual(results[0]['seed'], 5)
        self.assertEqual(results[0]['leech'], 0)
        self.assertEqual(results[0]['files'], 710)
        self.assertEqual(results[0]['magnetlink'], 'magnet:?xt=urn:btih:magnet&dn=Test')
        self.assertEqual(results[0]['filesize'], 1024)
        self.assertEqual(results[1]['filesize'], 1048576)
        self.assertEqual(results[2]['filesize'], 1073741824)
        self.assertEqual(results[3]['filesize'], 1099511627776)
