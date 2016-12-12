# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import youtube_noapi
from searx.testing import SearxTestCase


class TestYoutubeNoAPIEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['time_range'] = ''
        params = youtube_noapi.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('youtube.com', params['url'])

    def test_time_range_search(self):
        dicto = defaultdict(dict)
        query = 'test_query'
        dicto['time_range'] = 'year'
        params = youtube_noapi.request(query, dicto)
        self.assertIn('&sp=EgIIBQ%253D%253D', params['url'])

        dicto['time_range'] = 'month'
        params = youtube_noapi.request(query, dicto)
        self.assertIn('&sp=EgIIBA%253D%253D', params['url'])

        dicto['time_range'] = 'week'
        params = youtube_noapi.request(query, dicto)
        self.assertIn('&sp=EgIIAw%253D%253D', params['url'])

        dicto['time_range'] = 'day'
        params = youtube_noapi.request(query, dicto)
        self.assertIn('&sp=EgIIAg%253D%253D', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, youtube_noapi.response, None)
        self.assertRaises(AttributeError, youtube_noapi.response, [])
        self.assertRaises(AttributeError, youtube_noapi.response, '')
        self.assertRaises(AttributeError, youtube_noapi.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(youtube_noapi.response(response), [])

        html = """
        <ol id="item-section-063864" class="item-section">
            <li>
                <div class="yt-lockup yt-lockup-tile yt-lockup-video vve-check clearfix yt-uix-tile"
                data-context-item-id="DIVZCPfAOeM"
                data-visibility-tracking="CBgQ3DAYACITCPGXnYau6sUCFZEIHAod-VQASCj0JECx_-GK5uqMpcIB">
                <div class="yt-lockup-dismissable"><div class="yt-lockup-thumbnail contains-addto">
                <a aria-hidden="true" href="/watch?v=DIVZCPfAOeM" class=" yt-uix-sessionlink pf-link"
                data-sessionlink="itct=CBgQ3DAYACITCPGXnYau6sUCFZEIHAod-VQASCj0JFIEdGVzdA">
                <div class="yt-thumb video-thumb"><img src="//i.ytimg.com/vi/DIVZCPfAOeM/mqdefault.jpg"
                width="196" height="110"/></div><span class="video-time" aria-hidden="true">11:35</span></a>
                <span class="thumb-menu dark-overflow-action-menu video-actions">
                </span>
                </div>
                <div class="yt-lockup-content">
                <h3 class="yt-lockup-title">
                <a href="/watch?v=DIVZCPfAOeM"
                class="yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink spf-link"
                data-sessionlink="itct=CBgQ3DAYACITCPGXnYau6sUCFZEIHAod-VQASCj0JFIEdGVzdA"
                title="Top Speed Test Kawasaki Ninja H2 (Thailand) By. MEHAY SUPERBIKE"
                aria-describedby="description-id-259079" rel="spf-prefetch" dir="ltr">
                Title
                </a>
                <span class="accessible-description" id="description-id-259079"> - Durée : 11:35.</span>
                </h3>
                <div class="yt-lockup-byline">de
                <a href="/user/mheejapan" class=" yt-uix-sessionlink spf-link g-hovercard"
                data-sessionlink="itct=CBgQ3DAYACITCPGXnYau6sUCFZEIHAod-VQASCj0JA" data-ytid="UCzEesu54Hjs0uRKmpy66qeA"
                data-name="">MEHAY SUPERBIKE</a></div><div class="yt-lockup-meta">
                <ul class="yt-lockup-meta-info">
                    <li>il y a 20 heures</li>
                    <li>8 424 vues</li>
                </ul>
                </div>
                <div class="yt-lockup-description yt-ui-ellipsis yt-ui-ellipsis-2" dir="ltr">
                Description
                </div>
                <div class="yt-lockup-badges">
                <ul class="yt-badge-list ">
                    <li class="yt-badge-item" >
                        <span class="yt-badge">Nouveauté</span>
                    </li>
                    <li class="yt-badge-item" ><span class="yt-badge " >HD</span></li>
                </ul>
                </div>
                <div class="yt-lockup-action-menu yt-uix-menu-container">
                <div class="yt-uix-menu yt-uix-videoactionmenu hide-until-delayloaded"
                data-video-id="DIVZCPfAOeM" data-menu-content-id="yt-uix-videoactionmenu-menu">
                </div>
                </div>
                </div>
                </div>
                </div>
            </li>
        </ol>
        """
        response = mock.Mock(text=html)
        results = youtube_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'https://www.youtube.com/watch?v=DIVZCPfAOeM')
        self.assertEqual(results[0]['content'], 'Description')
        self.assertEqual(results[0]['thumbnail'], 'https://i.ytimg.com/vi/DIVZCPfAOeM/hqdefault.jpg')
        self.assertTrue('DIVZCPfAOeM' in results[0]['embedded'])

        html = """
        <ol id="item-section-063864" class="item-section">
            <li>
                <div class="yt-lockup yt-lockup-tile yt-lockup-video vve-check clearfix yt-uix-tile"
                data-context-item-id="DIVZCPfAOeM"
                data-visibility-tracking="CBgQ3DAYACITCPGXnYau6sUCFZEIHAod-VQASCj0JECx_-GK5uqMpcIB">
                <div class="yt-lockup-dismissable"><div class="yt-lockup-thumbnail contains-addto">
                <a aria-hidden="true" href="/watch?v=DIVZCPfAOeM" class=" yt-uix-sessionlink pf-link"
                data-sessionlink="itct=CBgQ3DAYACITCPGXnYau6sUCFZEIHAod-VQASCj0JFIEdGVzdA">
                <div class="yt-thumb video-thumb"><img src="//i.ytimg.com/vi/DIVZCPfAOeM/mqdefault.jpg"
                width="196" height="110"/></div><span class="video-time" aria-hidden="true">11:35</span></a>
                <span class="thumb-menu dark-overflow-action-menu video-actions">
                </span>
                </div>
                <div class="yt-lockup-content">
                <h3 class="yt-lockup-title">
                <span class="accessible-description" id="description-id-259079"> - Durée : 11:35.</span>
                </h3>
                <div class="yt-lockup-byline">de
                <a href="/user/mheejapan" class=" yt-uix-sessionlink spf-link g-hovercard"
                data-sessionlink="itct=CBgQ3DAYACITCPGXnYau6sUCFZEIHAod-VQASCj0JA" data-ytid="UCzEesu54Hjs0uRKmpy66qeA"
                data-name="">MEHAY SUPERBIKE</a></div><div class="yt-lockup-meta">
                <ul class="yt-lockup-meta-info">
                    <li>il y a 20 heures</li>
                    <li>8 424 vues</li>
                </ul>
                </div>
                <div class="yt-lockup-badges">
                <ul class="yt-badge-list ">
                    <li class="yt-badge-item" >
                        <span class="yt-badge">Nouveauté</span>
                    </li>
                    <li class="yt-badge-item" ><span class="yt-badge " >HD</span></li>
                </ul>
                </div>
                <div class="yt-lockup-action-menu yt-uix-menu-container">
                <div class="yt-uix-menu yt-uix-videoactionmenu hide-until-delayloaded"
                data-video-id="DIVZCPfAOeM" data-menu-content-id="yt-uix-videoactionmenu-menu">
                </div>
                </div>
                </div>
                </div>
                </div>
            </li>
        </ol>
        """
        response = mock.Mock(text=html)
        results = youtube_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)

        html = """
        <ol id="item-section-063864" class="item-section">
            <li>
            </li>
        </ol>
        """
        response = mock.Mock(text=html)
        results = youtube_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
