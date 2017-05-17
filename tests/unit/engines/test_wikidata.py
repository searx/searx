# -*- coding: utf-8 -*-
from lxml.html import fromstring
from collections import defaultdict
import mock
from searx.engines import wikidata
from searx.testing import SearxTestCase


class TestWikidataEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['language'] = 'all'
        params = wikidata.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('wikidata.org', params['url'])
        self.assertIn('en', params['url'])

        dicto['language'] = 'es_ES'
        params = wikidata.request(query, dicto)
        self.assertIn(query, params['url'])
        self.assertIn('es', params['url'])

    # successful cases are not tested here to avoid sending additional requests
    def test_response(self):
        self.assertRaises(AttributeError, wikidata.response, None)
        self.assertRaises(AttributeError, wikidata.response, [])
        self.assertRaises(AttributeError, wikidata.response, '')
        self.assertRaises(AttributeError, wikidata.response, '[]')

        response = mock.Mock(text='<html></html>', search_params={"language": "all"})
        self.assertEqual(wikidata.response(response), [])

    def test_getDetail(self):
        response = {}
        results = wikidata.getDetail(response, "Q123", "en", "en-US")
        self.assertEqual(results, [])

        title_html = '<div><div class="wikibase-title-label">Test</div></div>'
        html = """
        <div>
            <div class="wikibase-entitytermsview-heading-description">
            </div>
            <div>
                <ul class="wikibase-sitelinklistview-listview">
                    <li data-wb-siteid="enwiki"><a href="http://en.wikipedia.org/wiki/Test">Test</a></li>
                </ul>
            </div>
        </div>
        """
        response = {"parse": {"displaytitle": title_html, "text": html}}

        results = wikidata.getDetail(response, "Q123", "en", "en-US")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['url'], 'https://en.wikipedia.org/wiki/Test')

        title_html = """
        <div>
            <div class="wikibase-title-label">
                <span lang="en">Test</span>
                <sup class="wb-language-fallback-indicator">English</sup>
            </div>
        </div>
        """
        html = """
        <div>
            <div class="wikibase-entitytermsview-heading-description">
                <span lang="en">Description</span>
                <sup class="wb-language-fallback-indicator">English</sup>
            </div>
            <div id="P856">
                <div class="wikibase-statementgroupview-property-label">
                    <a href="/wiki/Property:P856">
                        <span lang="en">official website</span>
                        <sup class="wb-language-fallback-indicator">English</sup>
                    </a>
                </div>
                <div class="wikibase-statementview-mainsnak">
                    <a class="external free" href="https://officialsite.com">
                        https://officialsite.com
                    </a>
                </div>
            </div>
            <div>
                <ul class="wikibase-sitelinklistview-listview">
                    <li data-wb-siteid="enwiki"><a href="http://en.wikipedia.org/wiki/Test">Test</a></li>
                </ul>
            </div>
        </div>
        """
        response = {"parse": {"displaytitle": title_html, "text": html}}

        results = wikidata.getDetail(response, "Q123", "yua", "yua_MX")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Official website')
        self.assertEqual(results[0]['url'], 'https://officialsite.com')

        self.assertEqual(results[1]['infobox'], 'Test')
        self.assertEqual(results[1]['id'], None)
        self.assertEqual(results[1]['content'], 'Description')
        self.assertEqual(results[1]['attributes'], [])
        self.assertEqual(results[1]['urls'][0]['title'], 'Official website')
        self.assertEqual(results[1]['urls'][0]['url'], 'https://officialsite.com')
        self.assertEqual(results[1]['urls'][1]['title'], 'Wikipedia (en)')
        self.assertEqual(results[1]['urls'][1]['url'], 'https://en.wikipedia.org/wiki/Test')

    def test_add_image(self):
        image_src = wikidata.add_image(fromstring("<div></div>"))
        self.assertEqual(image_src, None)

        html = u"""
        <div>
            <div id="P18">
                <div class="wikibase-statementgroupview-property-label">
                    <a href="/wiki/Property:P18">
                        image
                    </a>
                </div>
                <div class="wikibase-statementlistview">
                    <div class="wikibase-statementview listview-item">
                        <div class="wikibase-statementview-rankselector">
                            <span class="wikibase-rankselector-normal"></span>
                        </div>
                        <div class="wikibase-statementview-mainsnak">
                            <div>
                                <div class="wikibase-snakview-value">
                                    <a href="https://commons.wikimedia.org/wiki/File:image.png">
                                        image.png
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        html_etree = fromstring(html)

        image_src = wikidata.add_image(html_etree)
        self.assertEqual(image_src,
                         "https://commons.wikimedia.org/wiki/Special:FilePath/image.png?width=500&height=400")

        html = u"""
        <div>
            <div id="P2910">
                <div class="wikibase-statementgroupview-property-label">
                    <a href="/wiki/Property:P2910">
                        icon
                    </a>
                </div>
                <div class="wikibase-statementlistview">
                    <div class="wikibase-statementview listview-item">
                        <div class="wikibase-statementview-rankselector">
                            <span class="wikibase-rankselector-normal"></span>
                        </div>
                        <div class="wikibase-statementview-mainsnak">
                            <div>
                                <div class="wikibase-snakview-value">
                                    <a href="https://commons.wikimedia.org/wiki/File:icon.png">
                                        icon.png
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div id="P154">
                <div class="wikibase-statementgroupview-property-label">
                    <a href="/wiki/Property:P154">
                        logo
                    </a>
                </div>
                <div class="wikibase-statementlistview">
                    <div class="wikibase-statementview listview-item">
                        <div class="wikibase-statementview-rankselector">
                            <span class="wikibase-rankselector-normal"></span>
                        </div>
                        <div class="wikibase-statementview-mainsnak">
                            <div>
                                <div class="wikibase-snakview-value">
                                    <a href="https://commons.wikimedia.org/wiki/File:logo.png">
                                        logo.png
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        html_etree = fromstring(html)

        image_src = wikidata.add_image(html_etree)
        self.assertEqual(image_src,
                         "https://commons.wikimedia.org/wiki/Special:FilePath/logo.png?width=500&height=400")

    def test_add_attribute(self):
        html = u"""
        <div>
            <div id="P27">
                <div class="wikibase-statementgroupview-property-label">
                    <a href="/wiki/Property:P27">
                        country of citizenship
                    </a>
                </div>
                <div class="wikibase-statementlistview">
                    <div class="wikibase-statementview listview-item">
                        <div class="wikibase-statementview-rankselector">
                            <span class="wikibase-rankselector-normal"></span>
                        </div>
                        <div class="wikibase-statementview-mainsnak">
                            <div>
                                <div class="wikibase-snakview-value">
                                    <a href="/wiki/Q145">
                                        United Kingdom
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        attributes = []
        html_etree = fromstring(html)

        wikidata.add_attribute(attributes, html_etree, "Fail")
        self.assertEqual(attributes, [])

        wikidata.add_attribute(attributes, html_etree, "P27")
        self.assertEqual(len(attributes), 1)
        self.assertEqual(attributes[0]["label"], "Country of citizenship")
        self.assertEqual(attributes[0]["value"], "United Kingdom")

        html = u"""
        <div>
            <div id="P569">
                <div class="wikibase-statementgroupview-property-label">
                    <a href="/wiki/Property:P569">
                        date of birth
                    </a>
                </div>
                <div class="wikibase-statementlistview">
                    <div class="wikibase-statementview listview-item">
                        <div class="wikibase-statementview-rankselector">
                            <span class="wikibase-rankselector-normal"></span>
                        </div>
                        <div class="wikibase-statementview-mainsnak">
                            <div>
                                <div class="wikibase-snakview-value">
                                    27 January 1832
                                    <sup class="wb-calendar-name">
                                        Gregorian
                                    </sup>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        attributes = []
        html_etree = fromstring(html)
        wikidata.add_attribute(attributes, html_etree, "P569", date=True)
        self.assertEqual(len(attributes), 1)
        self.assertEqual(attributes[0]["label"], "Date of birth")
        self.assertEqual(attributes[0]["value"], "27 January 1832")

        html = u"""
        <div>
            <div id="P6">
                <div class="wikibase-statementgroupview-property-label">
                    <a href="/wiki/Property:P27">
                        head of government
                    </a>
                </div>
                <div class="wikibase-statementlistview">
                    <div class="wikibase-statementview listview-item">
                        <div class="wikibase-statementview-rankselector">
                            <span class="wikibase-rankselector-normal"></span>
                        </div>
                        <div class="wikibase-statementview-mainsnak">
                            <div>
                                <div class="wikibase-snakview-value">
                                    <a href="/wiki/Q206">
                                        Old Prime Minister
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="wikibase-statementview listview-item">
                        <div class="wikibase-statementview-rankselector">
                            <span class="wikibase-rankselector-preferred"></span>
                        </div>
                        <div class="wikibase-statementview-mainsnak">
                            <div>
                                <div class="wikibase-snakview-value">
                                    <a href="/wiki/Q3099714">
                                        Actual Prime Minister
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        attributes = []
        html_etree = fromstring(html)
        wikidata.add_attribute(attributes, html_etree, "P6")
        self.assertEqual(len(attributes), 1)
        self.assertEqual(attributes[0]["label"], "Head of government")
        self.assertEqual(attributes[0]["value"], "Old Prime Minister, Actual Prime Minister")

        attributes = []
        html_etree = fromstring(html)
        wikidata.add_attribute(attributes, html_etree, "P6", trim=True)
        self.assertEqual(len(attributes), 1)
        self.assertEqual(attributes[0]["value"], "Actual Prime Minister")

    def test_add_url(self):
        html = u"""
        <div>
            <div id="P856">
                <div class="wikibase-statementgroupview-property-label">
                    <a href="/wiki/Property:P856">
                        official website
                    </a>
                </div>
                <div class="wikibase-statementlistview">
                    <div class="wikibase-statementview listview-item">
                        <div class="wikibase-statementview-mainsnak">
                            <div>
                                <div class="wikibase-snakview-value">
                                    <a class="external free" href="https://searx.me">
                                        https://searx.me/
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        urls = []
        html_etree = fromstring(html)
        wikidata.add_url(urls, html_etree, 'P856')
        self.assertEquals(len(urls), 1)
        self.assertIn({'title': 'Official website', 'url': 'https://searx.me/'}, urls)
        urls = []
        results = []
        wikidata.add_url(urls, html_etree, 'P856', 'custom label', results=results)
        self.assertEquals(len(urls), 1)
        self.assertEquals(len(results), 1)
        self.assertIn({'title': 'custom label', 'url': 'https://searx.me/'}, urls)
        self.assertIn({'title': 'custom label', 'url': 'https://searx.me/'}, results)

        html = u"""
        <div>
            <div id="P856">
                <div class="wikibase-statementgroupview-property-label">
                    <a href="/wiki/Property:P856">
                        official website
                    </a>
                </div>
                <div class="wikibase-statementlistview">
                    <div class="wikibase-statementview listview-item">
                        <div class="wikibase-statementview-mainsnak">
                            <div>
                                <div class="wikibase-snakview-value">
                                    <a class="external free" href="http://www.worldofwarcraft.com">
                                        http://www.worldofwarcraft.com
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="wikibase-statementview listview-item">
                        <div class="wikibase-statementview-mainsnak">
                            <div>
                                <div class="wikibase-snakview-value">
                                    <a class="external free" href="http://eu.battle.net/wow/en/">
                                        http://eu.battle.net/wow/en/
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        urls = []
        html_etree = fromstring(html)
        wikidata.add_url(urls, html_etree, 'P856')
        self.assertEquals(len(urls), 2)
        self.assertIn({'title': 'Official website', 'url': 'http://www.worldofwarcraft.com'}, urls)
        self.assertIn({'title': 'Official website', 'url': 'http://eu.battle.net/wow/en/'}, urls)

    def test_get_imdblink(self):
        html = u"""
        <div>
            <div class="wikibase-statementview-mainsnak">
                <div>
                    <div class="wikibase-snakview-value">
                        <a class="wb-external-id" href="http://www.imdb.com/tt0433664">
                            tt0433664
                        </a>
                    </div>
                </div>
            </div>
        </div>
        """
        html_etree = fromstring(html)
        imdblink = wikidata.get_imdblink(html_etree, 'https://www.imdb.com/')

        html = u"""
        <div>
            <div class="wikibase-statementview-mainsnak">
                <div>
                    <div class="wikibase-snakview-value">
                        <a class="wb-external-id"
                           href="href="http://tools.wmflabs.org/...http://www.imdb.com/&id=nm4915994"">
                            nm4915994
                        </a>
                    </div>
                </div>
            </div>
        </div>
        """
        html_etree = fromstring(html)
        imdblink = wikidata.get_imdblink(html_etree, 'https://www.imdb.com/')
        self.assertIn('https://www.imdb.com/name/nm4915994', imdblink)

    def test_get_geolink(self):
        html = u"""
        <div>
            <div class="wikibase-statementview-mainsnak">
                <div>
                    <div class="wikibase-snakview-value">
                        60°N, 40°E
                    </div>
                </div>
            </div>
        </div>
        """
        html_etree = fromstring(html)
        geolink = wikidata.get_geolink(html_etree)
        self.assertIn('https://www.openstreetmap.org/', geolink)
        self.assertIn('lat=60&lon=40', geolink)

        html = u"""
        <div>
            <div class="wikibase-statementview-mainsnak">
                <div>
                    <div class="wikibase-snakview-value">
                        34°35'59"S, 58°22'55"W
                    </div>
                </div>
            </div>
        </div>
        """
        html_etree = fromstring(html)
        geolink = wikidata.get_geolink(html_etree)
        self.assertIn('https://www.openstreetmap.org/', geolink)
        self.assertIn('lat=-34.59', geolink)
        self.assertIn('lon=-58.38', geolink)

    def test_get_wikilink(self):
        html = """
        <div>
            <div>
                <ul class="wikibase-sitelinklistview-listview">
                    <li data-wb-siteid="arwiki"><a href="http://ar.wikipedia.org/wiki/Test">Test</a></li>
                    <li data-wb-siteid="enwiki"><a href="http://en.wikipedia.org/wiki/Test">Test</a></li>
                </ul>
            </div>
            <div>
                <ul class="wikibase-sitelinklistview-listview">
                    <li data-wb-siteid="enwikiquote"><a href="https://en.wikiquote.org/wiki/Test">Test</a></li>
                </ul>
            </div>
        </div>
        """
        html_etree = fromstring(html)
        wikilink = wikidata.get_wikilink(html_etree, 'nowiki')
        self.assertEqual(wikilink, None)
        wikilink = wikidata.get_wikilink(html_etree, 'enwiki')
        self.assertEqual(wikilink, 'https://en.wikipedia.org/wiki/Test')
        wikilink = wikidata.get_wikilink(html_etree, 'arwiki')
        self.assertEqual(wikilink, 'https://ar.wikipedia.org/wiki/Test')
        wikilink = wikidata.get_wikilink(html_etree, 'enwikiquote')
        self.assertEqual(wikilink, 'https://en.wikiquote.org/wiki/Test')
