from collections import defaultdict
import mock
from searx.engines import youtube
from searx.testing import SearxTestCase


class TestYoutubeEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['language'] = 'fr_FR'
        params = youtube.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('youtube.com' in params['url'])
        self.assertTrue('fr' in params['url'])

        dicto['language'] = 'all'
        params = youtube.request(query, dicto)
        self.assertFalse('fr' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, youtube.response, None)
        self.assertRaises(AttributeError, youtube.response, [])
        self.assertRaises(AttributeError, youtube.response, '')
        self.assertRaises(AttributeError, youtube.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(youtube.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(youtube.response(response), [])

        json = """
        {"feed":{"entry":[{
            "id":{"$t":"http://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM"},
            "published":{"$t":"2015-01-23T21:25:00.000Z"},
            "updated":{"$t":"2015-01-26T14:38:15.000Z"},
            "title":{"$t":"Title",
                "type":"text"},"content":{"$t":"Description","type":"text"},
            "link":[{"rel":"alternate","type":"text/html",
                "href":"https://www.youtube.com/watch?v=DIVZCPfAOeM&feature=youtube_gdata"},
                {"rel":"http://gdata.youtube.com/schemas/2007#video.related",
                "type":"application/atom+xml",
                "href":"https://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM/related"},
                {"rel":"http://gdata.youtube.com/schemas/2007#mobile","type":"text/html",
                "href":"https://m.youtube.com/details?v=DIVZCPfAOeM"},
                {"rel":"self","type":"application/atom+xml",
                "href":"https://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM"}],
            "author":[{"name":{"$t":"Cauet"},
                "uri":{"$t":"https://gdata.youtube.com/feeds/api/users/cauetofficiel"} }],
            "gd$comments":{"gd$feedLink":{"rel":"http://gdata.youtube.com/schemas/2007#comments",
                "href":"https://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM/comments",
                "countHint":8} },
            "media$group":{"media$category":[{"$t":"Comedy","label":"Comedy",
                "scheme":"http://gdata.youtube.com/schemas/2007/categories.cat"}],
            "media$content":[{"url":"https://www.youtube.com/v/DIVZCPfAOeM?version=3&f=videos&app=youtube_gdata",
                "type":"application/x-shockwave-flash","medium":"video",
                "isDefault":"true","expression":"full","duration":354,"yt$format":5},
    {"url":"rtsp://r1---sn-cg07luel.c.youtube.com/CiILENy73wIaGQnjOcD3CFmFDBMYDSANFEgGUgZ2aWRlb3MM/0/0/0/video.3gp",
                "type":"video/3gpp","medium":"video","expression":"full","duration":354,
                "yt$format":1},
    {"url":"rtsp://r1---sn-cg07luel.c.youtube.com/CiILENy73wIaGQnjOcD3CFmFDBMYESARFEgGUgZ2aWRlb3MM/0/0/0/video.3gp",
                "type":"video/3gpp","medium":"video","expression":"full","duration":354,"yt$format":6}],
            "media$description":{"$t":"Desc","type":"plain"},
            "media$keywords":{},
            "media$player":[{"url":"https://www.youtube.com/watch?v=DIVZCPfAOeM&feature=youtube_gdata_player"}],
            "media$thumbnail":[{"url":"https://i.ytimg.com/vi/DIVZCPfAOeM/0.jpg",
                    "height":360,"width":480,"time":"00:02:57"},
                {"url":"https://i.ytimg.com/vi/DIVZCPfAOeM/1.jpg","height":90,"width":120,"time":"00:01:28.500"},
                {"url":"https://i.ytimg.com/vi/DIVZCPfAOeM/2.jpg","height":90,"width":120,"time":"00:02:57"},
                {"url":"https://i.ytimg.com/vi/DIVZCPfAOeM/3.jpg","height":90,"width":120,"time":"00:04:25.500"}],
            "media$title":{"$t":"Title","type":"plain"},
            "yt$duration":{"seconds":"354"} },
            "gd$rating":{"average":4.932159,"max":5,"min":1,"numRaters":1533,
                "rel":"http://schemas.google.com/g/2005#overall"},
            "yt$statistics":{"favoriteCount":"0","viewCount":"92464"} }
            ]
        }
        }
        """
        response = mock.Mock(text=json)
        results = youtube.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'https://www.youtube.com/watch?v=DIVZCPfAOeM')
        self.assertEqual(results[0]['content'], 'Description')
        self.assertEqual(results[0]['thumbnail'], 'https://i.ytimg.com/vi/DIVZCPfAOeM/0.jpg')
        self.assertTrue('DIVZCPfAOeM' in results[0]['embedded'])

        json = """
        {"feed":{"entry":[{
            "id":{"$t":"http://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM"},
            "published":{"$t":"2015-01-23T21:25:00.000Z"},
            "updated":{"$t":"2015-01-26T14:38:15.000Z"},
            "title":{"$t":"Title",
                "type":"text"},"content":{"$t":"Description","type":"text"},
            "link":[{"rel":"http://gdata.youtube.com/schemas/2007#video.related",
                "type":"application/atom+xml",
                "href":"https://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM/related"},
                {"rel":"self","type":"application/atom+xml",
                "href":"https://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM"}],
            "author":[{"name":{"$t":"Cauet"},
                "uri":{"$t":"https://gdata.youtube.com/feeds/api/users/cauetofficiel"} }],
            "gd$comments":{"gd$feedLink":{"rel":"http://gdata.youtube.com/schemas/2007#comments",
                "href":"https://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM/comments",
                "countHint":8} },
            "media$group":{"media$category":[{"$t":"Comedy","label":"Comedy",
                "scheme":"http://gdata.youtube.com/schemas/2007/categories.cat"}],
            "media$content":[{"url":"https://www.youtube.com/v/DIVZCPfAOeM?version=3&f=videos&app=youtube_gdata",
                "type":"application/x-shockwave-flash","medium":"video",
                "isDefault":"true","expression":"full","duration":354,"yt$format":5},
    {"url":"rtsp://r1---sn-cg07luel.c.youtube.com/CiILENy73wIaGQnjOcD3CFmFDBMYDSANFEgGUgZ2aWRlb3MM/0/0/0/video.3gp",
                "type":"video/3gpp","medium":"video","expression":"full","duration":354,
                "yt$format":1},
    {"url":"rtsp://r1---sn-cg07luel.c.youtube.com/CiILENy73wIaGQnjOcD3CFmFDBMYESARFEgGUgZ2aWRlb3MM/0/0/0/video.3gp",
                "type":"video/3gpp","medium":"video","expression":"full","duration":354,"yt$format":6}],
            "media$description":{"$t":"Desc","type":"plain"},
            "media$keywords":{},
            "media$player":[{"url":"https://www.youtube.com/watch?v=DIVZCPfAOeM&feature=youtube_gdata_player"}],
            "media$thumbnail":[{"url":"https://i.ytimg.com/vi/DIVZCPfAOeM/0.jpg",
                    "height":360,"width":480,"time":"00:02:57"},
                {"url":"https://i.ytimg.com/vi/DIVZCPfAOeM/1.jpg","height":90,"width":120,"time":"00:01:28.500"},
                {"url":"https://i.ytimg.com/vi/DIVZCPfAOeM/2.jpg","height":90,"width":120,"time":"00:02:57"},
                {"url":"https://i.ytimg.com/vi/DIVZCPfAOeM/3.jpg","height":90,"width":120,"time":"00:04:25.500"}],
            "media$title":{"$t":"Title","type":"plain"},
            "yt$duration":{"seconds":"354"} },
            "gd$rating":{"average":4.932159,"max":5,"min":1,"numRaters":1533,
                "rel":"http://schemas.google.com/g/2005#overall"},
            "yt$statistics":{"favoriteCount":"0","viewCount":"92464"} }
            ]
        }
        }
        """
        response = mock.Mock(text=json)
        results = youtube.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {"feed":{"entry":[{
            "id":{"$t":"http://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM"},
            "published":{"$t":"2015-01-23T21:25:00.000Z"},
            "updated":{"$t":"2015-01-26T14:38:15.000Z"},
            "title":{"$t":"Title",
                "type":"text"},"content":{"$t":"Description","type":"text"},
            "link":[{"rel":"alternate","type":"text/html",
                "href":"https://www.youtube.com/watch?v=DIVZCPfAOeM"},
                {"rel":"http://gdata.youtube.com/schemas/2007#video.related",
                "type":"application/atom+xml",
                "href":"https://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM/related"},
                {"rel":"http://gdata.youtube.com/schemas/2007#mobile","type":"text/html",
                "href":"https://m.youtube.com/details?v=DIVZCPfAOeM"},
                {"rel":"self","type":"application/atom+xml",
                "href":"https://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM"}],
            "author":[{"name":{"$t":"Cauet"},
                "uri":{"$t":"https://gdata.youtube.com/feeds/api/users/cauetofficiel"} }],
            "gd$comments":{"gd$feedLink":{"rel":"http://gdata.youtube.com/schemas/2007#comments",
                "href":"https://gdata.youtube.com/feeds/api/videos/DIVZCPfAOeM/comments",
                "countHint":8} },
            "media$group":{"media$category":[{"$t":"Comedy","label":"Comedy",
                "scheme":"http://gdata.youtube.com/schemas/2007/categories.cat"}],
            "media$content":[{"url":"https://www.youtube.com/v/DIVZCPfAOeM?version=3&f=videos&app=youtube_gdata",
                "type":"application/x-shockwave-flash","medium":"video",
                "isDefault":"true","expression":"full","duration":354,"yt$format":5},
    {"url":"rtsp://r1---sn-cg07luel.c.youtube.com/CiILENy73wIaGQnjOcD3CFmFDBMYDSANFEgGUgZ2aWRlb3MM/0/0/0/video.3gp",
                "type":"video/3gpp","medium":"video","expression":"full","duration":354,
                "yt$format":1},
    {"url":"rtsp://r1---sn-cg07luel.c.youtube.com/CiILENy73wIaGQnjOcD3CFmFDBMYESARFEgGUgZ2aWRlb3MM/0/0/0/video.3gp",
                "type":"video/3gpp","medium":"video","expression":"full","duration":354,"yt$format":6}],
            "media$description":{"$t":"Desc","type":"plain"},
            "media$keywords":{},
            "media$player":[{"url":"https://www.youtube.com/watch?v=DIVZCPfAOeM&feature=youtube_gdata_player"}],
            "media$title":{"$t":"Title","type":"plain"},
            "yt$duration":{"seconds":"354"} },
            "gd$rating":{"average":4.932159,"max":5,"min":1,"numRaters":1533,
                "rel":"http://schemas.google.com/g/2005#overall"},
            "yt$statistics":{"favoriteCount":"0","viewCount":"92464"} }
            ]
        }
        }
        """
        response = mock.Mock(text=json)
        results = youtube.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title')
        self.assertEqual(results[0]['url'], 'https://www.youtube.com/watch?v=DIVZCPfAOeM')
        self.assertEqual(results[0]['content'], 'Description')
        self.assertEqual(results[0]['thumbnail'], '')
        self.assertTrue('DIVZCPfAOeM' in results[0]['embedded'])

        json = """
        {"toto":{"entry":[]
        }
        }
        """
        response = mock.Mock(text=json)
        results = youtube.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
