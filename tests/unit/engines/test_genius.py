from collections import defaultdict
import mock
from datetime import datetime
from searx.engines import genius
from searx.testing import SearxTestCase


class TestGeniusEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = genius.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('genius.com' in params['url'])

    def test_response(self):

        json_empty = """
        {
        "meta": {
            "status": 200
        },
        "response": {
            "sections": [
            {
                "type": "top_hit",
                "hits": []
            },
            {
                "type": "song",
                "hits": []
            },
            {
                "type": "lyric",
                "hits": []
            },
            {
                "type": "artist",
                "hits": []
            },
            {
                "type": "album",
                "hits": []
            },
            {
                "type": "tag",
                "hits": []
            },
            {
                "type": "video",
                "hits": []
            },
            {
                "type": "article",
                "hits": []
            },
            {
                "type": "user",
                "hits": []
            }
            ]
        }
        }
        """

        resp = mock.Mock(text=json_empty)
        self.assertEqual(genius.response(resp), [])

        json = """
        {
        "meta": {
            "status": 200
        },
        "response": {
            "sections": [
            {
                "type": "lyric",
                "hits": [
                {
                    "highlights": [
                    {
                        "property": "lyrics",
                        "value": "Sample lyrics",
                        "snippet": true,
                        "ranges": []
                    }
                    ],
                    "index": "lyric",
                    "type": "song",
                    "result": {
                    "_type": "song",
                    "annotation_count": 45,
                    "api_path": "/songs/52916",
                    "full_title": "J't'emmerde by MC Jean Gab'1",
                    "header_image_thumbnail_url": "https://images.genius.com/ef9f736a86df3c3b1772f3fb7fbdb21c.300x300x1.jpg",
                    "header_image_url": "https://images.genius.com/ef9f736a86df3c3b1772f3fb7fbdb21c.1000x1000x1.jpg",
                    "id": 52916,
                    "instrumental": false,
                    "lyrics_owner_id": 15586,
                    "lyrics_state": "complete",
                    "lyrics_updated_at": 1498744545,
                    "path": "/Mc-jean-gab1-jtemmerde-lyrics",
                    "pyongs_count": 4,
                    "song_art_image_thumbnail_url": "https://images.genius.com/ef9f736a86df3c3b1772f3fb7fbdb21c.300x300x1.jpg",
                    "stats": {
                        "hot": false,
                        "unreviewed_annotations": 0,
                        "pageviews": 62490
                    },
                    "title": "J't'emmerde",
                    "title_with_featured": "J't'emmerde",
                    "updated_by_human_at": 1498744546,
                    "url": "https://genius.com/Mc-jean-gab1-jtemmerde-lyrics",
                    "primary_artist": {
                        "_type": "artist",
                        "api_path": "/artists/12691",
                        "header_image_url": "https://images.genius.com/c7847662a58f8c2b0f02a6e217d60907.960x657x1.jpg",
                        "id": 12691,
                        "image_url": "https://s3.amazonaws.com/rapgenius/Mc-jean-gab1.jpg",
                        "index_character": "m",
                        "is_meme_verified": false,
                        "is_verified": false,
                        "name": "MC Jean Gab'1",
                        "slug": "Mc-jean-gab1",
                        "url": "https://genius.com/artists/Mc-jean-gab1"
                    }
                    }
                }
                ]
            },
            {
                "type": "artist",
                "hits": [
                {
                    "highlights": [],
                    "index": "artist",
                    "type": "artist",
                    "result": {
                    "_type": "artist",
                    "api_path": "/artists/191580",
                    "header_image_url": "https://assets.genius.com/images/default_avatar_300.png?1503090542",
                    "id": 191580,
                    "image_url": "https://assets.genius.com/images/default_avatar_300.png?1503090542",
                    "index_character": "a",
                    "is_meme_verified": false,
                    "is_verified": false,
                    "name": "ASDF Guy",
                    "slug": "Asdf-guy",
                    "url": "https://genius.com/artists/Asdf-guy"
                    }
                }
                ]
            },
            {
                "type": "album",
                "hits": [
                {
                    "highlights": [],
                    "index": "album",
                    "type": "album",
                    "result": {
                    "_type": "album",
                    "api_path": "/albums/132332",
                    "cover_art_thumbnail_url": "https://images.genius.com/147d70434ba190b9b1c26b06aee87d17.300x300x1.jpg",
                    "cover_art_url": "https://images.genius.com/147d70434ba190b9b1c26b06aee87d17.600x600x1.jpg",
                    "full_title": "ASD by A Skylit Drive",
                    "id": 132332,
                    "name": "ASD",
                    "name_with_artist": "ASD (artist: A Skylit Drive)",
                    "release_date_components": {
                        "year": 2015,
                        "month": null,
                        "day": null
                    },
                    "url": "https://genius.com/albums/A-skylit-drive/Asd",
                    "artist": {
                        "_type": "artist",
                        "api_path": "/artists/48712",
                        "header_image_url": "https://images.genius.com/814c1551293172c56306d0e310c6aa89.620x400x1.jpg",
                        "id": 48712,
                        "image_url": "https://images.genius.com/814c1551293172c56306d0e310c6aa89.620x400x1.jpg",
                        "index_character": "s",
                        "is_meme_verified": false,
                        "is_verified": false,
                        "name": "A Skylit Drive",
                        "slug": "A-skylit-drive",
                        "url": "https://genius.com/artists/A-skylit-drive"
                    }
                    }
                }
                ]
            }
            ]
        }
        }
        """

        resp = mock.Mock(text=json)
        results = genius.response(resp)

        self.assertEqual(len(results), 3)
        self.assertEqual(type(results), list)

        # check lyric parsing
        r = results[0]
        self.assertEqual(r['url'], 'https://genius.com/Mc-jean-gab1-jtemmerde-lyrics')
        self.assertEqual(r['title'], "J't'emmerde by MC Jean Gab'1")
        self.assertEqual(r['content'], "Sample lyrics")
        self.assertEqual(r['template'], 'videos.html')
        self.assertEqual(r['thumbnail'], 'https://images.genius.com/ef9f736a86df3c3b1772f3fb7fbdb21c.300x300x1.jpg')
        created = datetime.fromtimestamp(1498744545)
        self.assertEqual(r['publishedDate'], created)

        # check artist parsing
        r = results[1]
        self.assertEqual(r['url'], 'https://genius.com/artists/Asdf-guy')
        self.assertEqual(r['title'], "ASDF Guy")
        self.assertEqual(r['content'], None)
        self.assertEqual(r['template'], 'videos.html')
        self.assertEqual(r['thumbnail'], 'https://assets.genius.com/images/default_avatar_300.png?1503090542')

        # check album parsing
        r = results[2]
        self.assertEqual(r['url'], 'https://genius.com/albums/A-skylit-drive/Asd')
        self.assertEqual(r['title'], "ASD by A Skylit Drive")
        self.assertEqual(r['content'], "Released: 2015")
        self.assertEqual(r['template'], 'videos.html')
        self.assertEqual(r['thumbnail'], 'https://images.genius.com/147d70434ba190b9b1c26b06aee87d17.600x600x1.jpg')
