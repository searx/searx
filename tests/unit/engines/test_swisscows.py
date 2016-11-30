from collections import defaultdict
import mock
from searx.engines import swisscows
from searx.testing import SearxTestCase


class TestSwisscowsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'de-DE'
        params = swisscows.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('swisscows.ch' in params['url'])
        self.assertTrue('uiLanguage=de' in params['url'])
        self.assertTrue('region=de-DE' in params['url'])

        dicto['language'] = 'all'
        params = swisscows.request(query, dicto)
        self.assertTrue('uiLanguage=browser' in params['url'])
        self.assertTrue('region=browser' in params['url'])

        dicto['category'] = 'images'
        params = swisscows.request(query, dicto)
        self.assertIn('image', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, swisscows.response, None)
        self.assertRaises(AttributeError, swisscows.response, [])
        self.assertRaises(AttributeError, swisscows.response, '')
        self.assertRaises(AttributeError, swisscows.response, '[]')

        response = mock.Mock(text=b'<html></html>')
        self.assertEqual(swisscows.response(response), [])

        response = mock.Mock(text=b'<html></html>')
        self.assertEqual(swisscows.response(response), [])

        html = b"""
        <script>
            App.Dispatcher.dispatch("initialize", {
                html5history: true,
                initialData: {"Request":
                    {"Page":1,
                    "ItemsCount":1,
                    "Query":"This should ",
                    "NormalizedQuery":"This should ",
                    "Region":"de-AT",
                    "UILanguage":"de"},
                    "Results":{"items":[
                            {"Title":"\uE000This should\uE001 be the title",
                            "Description":"\uE000This should\uE001 be the content.",
                            "Url":"http://this.should.be.the.link/",
                            "DisplayUrl":"www.\uE000this.should.be.the\uE001.link",
                            "Id":"782ef287-e439-451c-b380-6ebc14ba033d"},
                            {"Title":"Datei:This should1.svg",
                            "Url":"https://i.swisscows.ch/?link=http%3a%2f%2fts2.mm.This/should1.png",
                            "SourceUrl":"http://de.wikipedia.org/wiki/Datei:This should1.svg",
                            "DisplayUrl":"de.wikipedia.org/wiki/Datei:This should1.svg",
                            "Width":950,
                            "Height":534,
                            "FileSize":92100,
                            "ContentType":"image/jpeg",
                            "Thumbnail":{
                                "Url":"https://i.swisscows.ch/?link=http%3a%2f%2fts2.mm.This/should1.png",
                                "ContentType":"image/jpeg",
                                "Width":300,
                                "Height":168,
                                "FileSize":9134},
                                "Id":"6a97a542-8f65-425f-b7f6-1178c3aba7be"
                            }
                        ],"TotalCount":55300,
                        "Query":"This should "
                    },
                    "Images":[{"Title":"Datei:This should.svg",
                        "Url":"https://i.swisscows.ch/?link=http%3a%2f%2fts2.mm.This/should.png",
                        "SourceUrl":"http://de.wikipedia.org/wiki/Datei:This should.svg",
                        "DisplayUrl":"de.wikipedia.org/wiki/Datei:This should.svg",
                        "Width":1280,
                        "Height":677,
                        "FileSize":50053,
                        "ContentType":"image/png",
                        "Thumbnail":{"Url":"https://i.swisscows.ch/?link=http%3a%2f%2fts2.mm.This/should.png",
                            "ContentType":"image/png",
                            "Width":300,
                            "Height":158,
                            "FileSize":8023},
                        "Id":"ae230fd8-a06a-47d6-99d5-e74766d8143a"}]},
                environment: "production"
            }).then(function (options) {
                $('#Search_Form').on('submit', function (e) {
                    if (!Modernizr.history) return;
                    e.preventDefault();

                    var $form = $(this),
                        $query = $('#Query'),
                        query = $.trim($query.val()),
                        path = App.Router.makePath($form.attr('action'), null, $form.serializeObject())

                    if (query.length) {
                        options.html5history ?
                            ReactRouter.HistoryLocation.push(path) :
                            ReactRouter.RefreshLocation.push(path);
                    }
                    else $('#Query').trigger('blur');
                });

            });
        </script>
        """
        response = mock.Mock(text=html)
        results = swisscows.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'This should be the title')
        self.assertEqual(results[0]['url'], 'http://this.should.be.the.link/')
        self.assertEqual(results[0]['content'], 'This should be the content.')
        self.assertEqual(results[1]['title'], 'Datei:This should1.svg')
        self.assertEqual(results[1]['url'], 'http://de.wikipedia.org/wiki/Datei:This should1.svg')
        self.assertEqual(results[1]['img_src'], 'http://ts2.mm.This/should1.png')
        self.assertEqual(results[1]['template'], 'images.html')
        self.assertEqual(results[2]['title'], 'Datei:This should.svg')
        self.assertEqual(results[2]['url'], 'http://de.wikipedia.org/wiki/Datei:This should.svg')
        self.assertEqual(results[2]['img_src'], 'http://ts2.mm.This/should.png')
        self.assertEqual(results[2]['template'], 'images.html')

    def test_fetch_supported_languages(self):
        html = """<html></html>"""
        response = mock.Mock(text=html)
        languages = swisscows._fetch_supported_languages(response)
        self.assertEqual(type(languages), list)
        self.assertEqual(len(languages), 0)

        html = """
        <html>
            <div id="regions-popup">
                <div>
                    <ul>
                        <li><a data-val="browser"></a></li>
                        <li><a data-val="de-CH"></a></li>
                        <li><a data-val="fr-CH"></a></li>
                    </ul>
                </div>
            </div>
        </html>
        """
        response = mock.Mock(text=html)
        languages = swisscows._fetch_supported_languages(response)
        self.assertEqual(type(languages), list)
        self.assertEqual(len(languages), 3)
        self.assertIn('de-CH', languages)
        self.assertIn('fr-CH', languages)
