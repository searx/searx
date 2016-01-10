from collections import defaultdict
import mock
from searx.engines import google_news
from searx.testing import SearxTestCase


class TestGoogleNewsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        params = google_news.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('googleapis.com', params['url'])
        self.assertIn('fr', params['url'])

        dicto['language'] = 'all'
        params = google_news.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn('en', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, google_news.response, None)
        self.assertRaises(AttributeError, google_news.response, [])
        self.assertRaises(AttributeError, google_news.response, '')
        self.assertRaises(AttributeError, google_news.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(google_news.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(google_news.response(response), [])

        json = """
        {
        "responseData": {
            "results": [
            {
                "GsearchResultClass": "GnewsSearch",
                "clusterUrl": "http://news.google.com/news/story?ncl=d2d3t1LMDpNIj2MPPhdTT0ycN4sWM&hl=fr&ned=fr",
                "content": "This is the content",
                "unescapedUrl": "http://this.is.the.url",
                "url": "http://this.is.the.url",
                "title": "This is the title",
                "titleNoFormatting": "This is the title",
                "location": "",
                "publisher": "Jeux Actu",
                "publishedDate": "Fri, 30 Jan 2015 11:00:25 -0800",
                "signedRedirectUrl": "http://news.google.com/",
                "language": "fr",
                "image": {
                "url": "http://i.jeuxactus.com/datas/jeux/d/y/dying-light/vu/dying-light-54cc080b568fb.jpg",
                "tbUrl": "http://t1.gstatic.com/images?q=tbn:ANd9GcSF4yYrs9Ycw23DGiOSAZ-5SEPXYwG3LNs",
                "originalContextUrl": "http://www.jeuxactu.com/test-dying-light-sur-ps4-97208.htm",
                "publisher": "Jeux Actu",
                "tbWidth": 80,
                "tbHeight": 30
                },
                "relatedStories": [
                {
                    "unescapedUrl": "http://www.jeuxvideo.com/test/415823/dying-light.htm",
                    "url": "http%3A%2F%2Fwww.jeuxvideo.com%2Ftest%2F415823%2Fdying-light.htm",
                    "title": "<b>Test</b> du jeu Dying Light - jeuxvideo.com",
                    "titleNoFormatting": "Test du jeu Dying Light - jeuxvideo.com",
                    "location": "",
                    "publisher": "JeuxVideo.com",
                    "publishedDate": "Fri, 30 Jan 2015 08:52:30 -0800",
                    "signedRedirectUrl": "http://news.google.com/news/url?sa=T&",
                    "language": "fr"
                }
                ]
            }
            ]
        },
        "responseDetails": null,
        "responseStatus": 200
        }
        """
        response = mock.Mock(text=json)
        results = google_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url')
        self.assertEqual(results[0]['content'], 'This is the content')

        json = """
        {
        "responseData": {
            "results": [
            {
                "GsearchResultClass": "GnewsSearch",
                "clusterUrl": "http://news.google.com/news/story?ncl=d2d3t1LMDpNIj2MPPhdTT0ycN4sWM&hl=fr&ned=fr",
                "content": "This is the content",
                "unescapedUrl": "http://this.is.the.url",
                "title": "This is the title",
                "titleNoFormatting": "This is the title",
                "location": "",
                "publisher": "Jeux Actu",
                "publishedDate": "Fri, 30 Jan 2015 11:00:25 -0800",
                "signedRedirectUrl": "http://news.google.com/news/",
                "language": "fr",
                "image": {
                "url": "http://i.jeuxactus.com/datas/jeux/d/y/dying-light/vu/dying-light-54cc080b568fb.jpg",
                "tbUrl": "http://t1.gstatic.com/images?q=tbn:b_6f-OSAZ-5SEPXYwG3LNs",
                "originalContextUrl": "http://www.jeuxactu.com/test-dying-light-sur-ps4-97208.htm",
                "publisher": "Jeux Actu",
                "tbWidth": 80,
                "tbHeight": 30
                }
            }
            ]
        },
        "responseDetails": null,
        "responseStatus": 200
        }
        """
        response = mock.Mock(text=json)
        results = google_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {
        "responseData": {},
        "responseDetails": null,
        "responseStatus": 200
        }
        """
        response = mock.Mock(text=json)
        results = google_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
