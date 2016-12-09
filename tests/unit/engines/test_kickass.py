# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import kickass
from searx.testing import SearxTestCase


class TestKickassEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = kickass.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('kickass.cd', params['url'])
        self.assertFalse(params['verify'])

    def test_response(self):
        self.assertRaises(AttributeError, kickass.response, None)
        self.assertRaises(AttributeError, kickass.response, [])
        self.assertRaises(AttributeError, kickass.response, '')
        self.assertRaises(AttributeError, kickass.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(kickass.response(response), [])

        html = """
        <table cellpadding="0" cellspacing="0" class="data" style="width: 100%">
            <tr class="firstr">
                <th class="width100perc nopad">torrent name</th>
                <th class="center">
                    <a href="/search/test/?field=size&sorder=desc" rel="nofollow">size</a>
                </th>
                <th class="center"><span class="files">
                    <a href="/search/test/?field=files_count&sorder=desc" rel="nofollow">files</a></span>
                </th>
                <th class="center"><span>
                    <a href="/search/test/?field=time_add&sorder=desc" rel="nofollow">age</a></span>
                </th>
                <th class="center"><span class="seed">
                    <a href="/search/test/?field=seeders&sorder=desc" rel="nofollow">seed</a></span>
                </th>
                <th class="lasttd nobr center">
                    <a href="/search/test/?field=leechers&sorder=desc" rel="nofollow">leech</a>
                </th>
            </tr>
            <tr class="even" id="torrent_test6478745">
                <td>
                    <div class="iaconbox center floatright">
                        <a rel="6478745,0" class="icommentjs icon16" href="/test-t6478745.html#comment">
                            <em style="font-size: 12px; margin: 0 4px 0 4px;" class="iconvalue">3</em>
                            <i class="ka ka-comment"></i>
                        </a>
                        <a class="iverify icon16" href="/test-t6478745.html" title="Verified Torrent">
                            <i class="ka ka16 ka-verify ka-green"></i>
                        </a>
                        <a href="#" onclick="_scq.push([]); return false;" class="partner1Button idownload icon16">
                            <i class="ka ka16 ka-arrow-down partner1Button"></i>
                        </a>
                        <a title="Torrent magnet link"
                            href="magnet:?xt=urn:btih:MAGNETURL&dn=test" class="imagnet icon16">
                            <i class="ka ka16 ka-magnet"></i>
                        </a>
                        <a title="Download torrent file"
                            href="http://torcache.net/torrent/53917.torrent?title=test" class="idownload icon16">
                            <i class="ka ka16 ka-arrow-down"></i>
                        </a>
                    </div>
                    <div class="torrentname">
                    <a href="/test-t6478745.html" class="torType txtType"></a>
                    <a href="/test-t6478745.html" class="normalgrey font12px plain bold"></a>
                    <div class="markeredBlock torType txtType">
                        <a href="/url.html" class="cellMainLink">
                            <strong class="red">This should be the title</strong>
                        </a>
                        <span class="font11px lightgrey block">
                            Posted by <i class="ka ka-verify" style="font-size: 16px;color:orange;"></i>
                            <a class="plain" href="/user/riri/">riri</a> in
                            <span id="cat_6478745">
                                <strong><a href="/other/">Other</a> > <a href="/unsorted/">Unsorted</a></strong>
                            </span>
                        </span>
                    </div>
                </td>
                <td class="nobr center">449 bytes</td>
                <td class="center">4</td>
                <td class="center">2&nbsp;years</td>
                <td class="green center">10</td>
                <td class="red lasttd center">1</td>
            </tr>
        </table>
        """
        response = mock.Mock(text=html)
        results = kickass.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This should be the title')
        self.assertEqual(results[0]['url'], 'https://kickass.cd/url.html')
        self.assertEqual(results[0]['content'], 'Posted by riri in Other > Unsorted')
        self.assertEqual(results[0]['seed'], 10)
        self.assertEqual(results[0]['leech'], 1)
        self.assertEqual(results[0]['filesize'], 449)
        self.assertEqual(results[0]['files'], 4)
        self.assertEqual(results[0]['magnetlink'], 'magnet:?xt=urn:btih:MAGNETURL&dn=test')
        self.assertEqual(results[0]['torrentfile'], 'http://torcache.net/torrent/53917.torrent?title=test')

        html = """
        <table cellpadding="0" cellspacing="0" class="data" style="width: 100%">
            <tr class="firstr">
                <th class="width100perc nopad">torrent name</th>
                <th class="center">
                    <a href="/search/test/?field=size&sorder=desc" rel="nofollow">size</a>
                </th>
                <th class="center"><span class="files">
                    <a href="/search/test/?field=files_count&sorder=desc" rel="nofollow">files</a></span>
                </th>
                <th class="center"><span>
                    <a href="/search/test/?field=time_add&sorder=desc" rel="nofollow">age</a></span>
                </th>
                <th class="center"><span class="seed">
                    <a href="/search/test/?field=seeders&sorder=desc" rel="nofollow">seed</a></span>
                </th>
                <th class="lasttd nobr center">
                    <a href="/search/test/?field=leechers&sorder=desc" rel="nofollow">leech</a>
                </th>
            </tr>
        </table>
        """
        response = mock.Mock(text=html)
        results = kickass.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        html = """
        <table cellpadding="0" cellspacing="0" class="data" style="width: 100%">
            <tr class="firstr">
                <th class="width100perc nopad">torrent name</th>
                <th class="center">
                    <a href="/search/test/?field=size&sorder=desc" rel="nofollow">size</a>
                </th>
                <th class="center"><span class="files">
                    <a href="/search/test/?field=files_count&sorder=desc" rel="nofollow">files</a></span>
                </th>
                <th class="center"><span>
                    <a href="/search/test/?field=time_add&sorder=desc" rel="nofollow">age</a></span>
                </th>
                <th class="center"><span class="seed">
                    <a href="/search/test/?field=seeders&sorder=desc" rel="nofollow">seed</a></span>
                </th>
                <th class="lasttd nobr center">
                    <a href="/search/test/?field=leechers&sorder=desc" rel="nofollow">leech</a>
                </th>
            </tr>
            <tr class="even" id="torrent_test6478745">
                <td>
                    <div class="iaconbox center floatright">
                        <a rel="6478745,0" class="icommentjs icon16" href="/test-t6478745.html#comment">
                            <em style="font-size: 12px; margin: 0 4px 0 4px;" class="iconvalue">3</em>
                            <i class="ka ka-comment"></i>
                        </a>
                        <a class="iverify icon16" href="/test-t6478745.html" title="Verified Torrent">
                            <i class="ka ka16 ka-verify ka-green"></i>
                        </a>
                        <a href="#" onclick="_scq.push([]); return false;" class="partner1Button idownload icon16">
                            <i class="ka ka16 ka-arrow-down partner1Button"></i>
                        </a>
                        <a title="Torrent magnet link"
                            href="magnet:?xt=urn:btih:MAGNETURL&dn=test" class="imagnet icon16">
                            <i class="ka ka16 ka-magnet"></i>
                        </a>
                        <a title="Download torrent file"
                            href="http://torcache.net/torrent/53917.torrent?title=test" class="idownload icon16">
                            <i class="ka ka16 ka-arrow-down"></i>
                        </a>
                    </div>
                    <div class="torrentname">
                    <a href="/test-t6478745.html" class="torType txtType"></a>
                    <a href="/test-t6478745.html" class="normalgrey font12px plain bold"></a>
                    <div class="markeredBlock torType txtType">
                        <a href="/url.html" class="cellMainLink">
                            <strong class="red">This should be the title</strong>
                        </a>
                        <span class="font11px lightgrey block">
                            Posted by <i class="ka ka-verify" style="font-size: 16px;color:orange;"></i>
                            <a class="plain" href="/user/riri/">riri</a> in
                            <span id="cat_6478745">
                                <strong><a href="/other/">Other</a> > <a href="/unsorted/">Unsorted</a></strong>
                            </span>
                        </span>
                    </div>
                </td>
                <td class="nobr center">1 KiB</td>
                <td class="center">4</td>
                <td class="center">2&nbsp;years</td>
                <td class="green center">10</td>
                <td class="red lasttd center">1</td>
            </tr>
            <tr class="even" id="torrent_test6478745">
                <td>
                    <div class="iaconbox center floatright">
                        <a rel="6478745,0" class="icommentjs icon16" href="/test-t6478745.html#comment">
                            <em style="font-size: 12px; margin: 0 4px 0 4px;" class="iconvalue">3</em>
                            <i class="ka ka-comment"></i>
                        </a>
                        <a class="iverify icon16" href="/test-t6478745.html" title="Verified Torrent">
                            <i class="ka ka16 ka-verify ka-green"></i>
                        </a>
                        <a href="#" onclick="_scq.push([]); return false;" class="partner1Button idownload icon16">
                            <i class="ka ka16 ka-arrow-down partner1Button"></i>
                        </a>
                        <a title="Torrent magnet link"
                            href="magnet:?xt=urn:btih:MAGNETURL&dn=test" class="imagnet icon16">
                            <i class="ka ka16 ka-magnet"></i>
                        </a>
                        <a title="Download torrent file"
                            href="http://torcache.net/torrent/53917.torrent?title=test" class="idownload icon16">
                            <i class="ka ka16 ka-arrow-down"></i>
                        </a>
                    </div>
                    <div class="torrentname">
                    <a href="/test-t6478745.html" class="torType txtType"></a>
                    <a href="/test-t6478745.html" class="normalgrey font12px plain bold"></a>
                    <div class="markeredBlock torType txtType">
                        <a href="/url.html" class="cellMainLink">
                            <strong class="red">This should be the title</strong>
                        </a>
                        <span class="font11px lightgrey block">
                            Posted by <i class="ka ka-verify" style="font-size: 16px;color:orange;"></i>
                            <a class="plain" href="/user/riri/">riri</a> in
                            <span id="cat_6478745">
                                <strong><a href="/other/">Other</a> > <a href="/unsorted/">Unsorted</a></strong>
                            </span>
                        </span>
                    </div>
                </td>
                <td class="nobr center">1 MiB</td>
                <td class="center">4</td>
                <td class="center">2&nbsp;years</td>
                <td class="green center">9</td>
                <td class="red lasttd center">1</td>
            </tr>
            <tr class="even" id="torrent_test6478745">
                <td>
                    <div class="iaconbox center floatright">
                        <a rel="6478745,0" class="icommentjs icon16" href="/test-t6478745.html#comment">
                            <em style="font-size: 12px; margin: 0 4px 0 4px;" class="iconvalue">3</em>
                            <i class="ka ka-comment"></i>
                        </a>
                        <a class="iverify icon16" href="/test-t6478745.html" title="Verified Torrent">
                            <i class="ka ka16 ka-verify ka-green"></i>
                        </a>
                        <a href="#" onclick="_scq.push([]); return false;" class="partner1Button idownload icon16">
                            <i class="ka ka16 ka-arrow-down partner1Button"></i>
                        </a>
                        <a title="Torrent magnet link"
                            href="magnet:?xt=urn:btih:MAGNETURL&dn=test" class="imagnet icon16">
                            <i class="ka ka16 ka-magnet"></i>
                        </a>
                        <a title="Download torrent file"
                            href="http://torcache.net/torrent/53917.torrent?title=test" class="idownload icon16">
                            <i class="ka ka16 ka-arrow-down"></i>
                        </a>
                    </div>
                    <div class="torrentname">
                    <a href="/test-t6478745.html" class="torType txtType"></a>
                    <a href="/test-t6478745.html" class="normalgrey font12px plain bold"></a>
                    <div class="markeredBlock torType txtType">
                        <a href="/url.html" class="cellMainLink">
                            <strong class="red">This should be the title</strong>
                        </a>
                        <span class="font11px lightgrey block">
                            Posted by <i class="ka ka-verify" style="font-size: 16px;color:orange;"></i>
                            <a class="plain" href="/user/riri/">riri</a> in
                            <span id="cat_6478745">
                                <strong><a href="/other/">Other</a> > <a href="/unsorted/">Unsorted</a></strong>
                            </span>
                        </span>
                    </div>
                </td>
                <td class="nobr center">1 GiB</td>
                <td class="center">4</td>
                <td class="center">2&nbsp;years</td>
                <td class="green center">8</td>
                <td class="red lasttd center">1</td>
            </tr>
            <tr class="even" id="torrent_test6478745">
                <td>
                    <div class="iaconbox center floatright">
                        <a rel="6478745,0" class="icommentjs icon16" href="/test-t6478745.html#comment">
                            <em style="font-size: 12px; margin: 0 4px 0 4px;" class="iconvalue">3</em>
                            <i class="ka ka-comment"></i>
                        </a>
                        <a class="iverify icon16" href="/test-t6478745.html" title="Verified Torrent">
                            <i class="ka ka16 ka-verify ka-green"></i>
                        </a>
                        <a href="#" onclick="_scq.push([]); return false;" class="partner1Button idownload icon16">
                            <i class="ka ka16 ka-arrow-down partner1Button"></i>
                        </a>
                        <a title="Torrent magnet link"
                            href="magnet:?xt=urn:btih:MAGNETURL&dn=test" class="imagnet icon16">
                            <i class="ka ka16 ka-magnet"></i>
                        </a>
                        <a title="Download torrent file"
                            href="http://torcache.net/torrent/53917.torrent?title=test" class="idownload icon16">
                            <i class="ka ka16 ka-arrow-down"></i>
                        </a>
                    </div>
                    <div class="torrentname">
                    <a href="/test-t6478745.html" class="torType txtType"></a>
                    <a href="/test-t6478745.html" class="normalgrey font12px plain bold"></a>
                    <div class="markeredBlock torType txtType">
                        <a href="/url.html" class="cellMainLink">
                            <strong class="red">This should be the title</strong>
                        </a>
                        <span class="font11px lightgrey block">
                            Posted by <i class="ka ka-verify" style="font-size: 16px;color:orange;"></i>
                            <a class="plain" href="/user/riri/">riri</a> in
                            <span id="cat_6478745">
                                <strong><a href="/other/">Other</a> > <a href="/unsorted/">Unsorted</a></strong>
                            </span>
                        </span>
                    </div>
                </td>
                <td class="nobr center">1 TiB</td>
                <td class="center">4</td>
                <td class="center">2&nbsp;years</td>
                <td class="green center">7</td>
                <td class="red lasttd center">1</td>
            </tr>
            <tr class="even" id="torrent_test6478745">
                <td>
                    <div class="iaconbox center floatright">
                        <a rel="6478745,0" class="icommentjs icon16" href="/test-t6478745.html#comment">
                            <em style="font-size: 12px; margin: 0 4px 0 4px;" class="iconvalue">3</em>
                            <i class="ka ka-comment"></i>
                        </a>
                        <a class="iverify icon16" href="/test-t6478745.html" title="Verified Torrent">
                            <i class="ka ka16 ka-verify ka-green"></i>
                        </a>
                        <a href="#" onclick="_scq.push([]); return false;" class="partner1Button idownload icon16">
                            <i class="ka ka16 ka-arrow-down partner1Button"></i>
                        </a>
                        <a title="Torrent magnet link"
                            href="magnet:?xt=urn:btih:MAGNETURL&dn=test" class="imagnet icon16">
                            <i class="ka ka16 ka-magnet"></i>
                        </a>
                        <a title="Download torrent file"
                            href="http://torcache.net/torrent/53917.torrent?title=test" class="idownload icon16">
                            <i class="ka ka16 ka-arrow-down"></i>
                        </a>
                    </div>
                    <div class="torrentname">
                    <a href="/test-t6478745.html" class="torType txtType"></a>
                    <a href="/test-t6478745.html" class="normalgrey font12px plain bold"></a>
                    <div class="markeredBlock torType txtType">
                        <a href="/url.html" class="cellMainLink">
                            <strong class="red">This should be the title</strong>
                        </a>
                        <span class="font11px lightgrey block">
                            Posted by <i class="ka ka-verify" style="font-size: 16px;color:orange;"></i>
                            <a class="plain" href="/user/riri/">riri</a> in
                            <span id="cat_6478745">
                                <strong><a href="/other/">Other</a> > <a href="/unsorted/">Unsorted</a></strong>
                            </span>
                        </span>
                    </div>
                </td>
                <td class="nobr center">z bytes</td>
                <td class="center">r</td>
                <td class="center">2&nbsp;years</td>
                <td class="green center">a</td>
                <td class="red lasttd center">t</td>
            </tr>
        </table>
        """
        response = mock.Mock(text=html)
        results = kickass.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0]['title'], 'This should be the title')
        self.assertEqual(results[0]['url'], 'https://kickass.cd/url.html')
        self.assertEqual(results[0]['content'], 'Posted by riri in Other > Unsorted')
        self.assertEqual(results[0]['seed'], 10)
        self.assertEqual(results[0]['leech'], 1)
        self.assertEqual(results[0]['files'], 4)
        self.assertEqual(results[0]['magnetlink'], 'magnet:?xt=urn:btih:MAGNETURL&dn=test')
        self.assertEqual(results[0]['torrentfile'], 'http://torcache.net/torrent/53917.torrent?title=test')
        self.assertEqual(results[0]['filesize'], 1000)
        self.assertEqual(results[1]['filesize'], 1000000)
        self.assertEqual(results[2]['filesize'], 1000000000)
        self.assertEqual(results[3]['filesize'], 1000000000000)
        self.assertEqual(results[4]['seed'], 0)
        self.assertEqual(results[4]['leech'], 0)
        self.assertEqual(results[4]['files'], None)
        self.assertEqual(results[4]['filesize'], None)
