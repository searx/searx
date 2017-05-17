from collections import defaultdict
import mock
from searx.engines import soundcloud
from searx.testing import SearxTestCase
from searx.url_utils import quote_plus


class TestSoundcloudEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = soundcloud.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('soundcloud.com', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, soundcloud.response, None)
        self.assertRaises(AttributeError, soundcloud.response, [])
        self.assertRaises(AttributeError, soundcloud.response, '')
        self.assertRaises(AttributeError, soundcloud.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(soundcloud.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(soundcloud.response(response), [])

        json = """
        {
        "collection": [
            {
            "kind": "track",
            "id": 159723640,
            "created_at": "2014/07/22 00:51:21 +0000",
            "user_id": 2976616,
            "duration": 303780,
            "commentable": true,
            "state": "finished",
            "original_content_size": 13236349,
            "last_modified": "2015/01/31 15:14:50 +0000",
            "sharing": "public",
            "tag_list": "seekae flume",
            "permalink": "seekae-test-recognise-flume-re-work",
            "streamable": true,
            "embeddable_by": "all",
            "downloadable": true,
            "purchase_url": "http://www.facebook.com/seekaemusic",
            "label_id": null,
            "purchase_title": "Seekae",
            "genre": "freedownload",
            "title": "This is the title",
            "description": "This is the content",
            "label_name": "Future Classic",
            "release": "",
            "track_type": "remix",
            "key_signature": "",
            "isrc": "",
            "video_url": null,
            "bpm": null,
            "release_year": 2014,
            "release_month": 7,
            "release_day": 22,
            "original_format": "mp3",
            "license": "all-rights-reserved",
            "uri": "https://api.soundcloud.com/tracks/159723640",
            "user": {
                "id": 2976616,
                "kind": "user",
                "permalink": "flume",
                "username": "Flume",
                "last_modified": "2014/11/24 19:21:29 +0000",
                "uri": "https://api.soundcloud.com/users/2976616",
                "permalink_url": "http://soundcloud.com/flume",
                "avatar_url": "https://i1.sndcdn.com/avatars-000044475439-4zi7ii-large.jpg"
            },
            "permalink_url": "http://soundcloud.com/this.is.the.url",
            "artwork_url": "https://i1.sndcdn.com/artworks-000085857162-xdxy5c-large.jpg",
            "waveform_url": "https://w1.sndcdn.com/DWrL1lAN8BkP_m.png",
            "stream_url": "https://api.soundcloud.com/tracks/159723640/stream",
            "download_url": "https://api.soundcloud.com/tracks/159723640/download",
            "playback_count": 2190687,
            "download_count": 54856,
            "favoritings_count": 49061,
            "comment_count": 826,
            "likes_count": 49061,
            "reposts_count": 15910,
            "attachments_uri": "https://api.soundcloud.com/tracks/159723640/attachments",
            "policy": "ALLOW"
            }
        ],
        "total_results": 375750,
        "next_href": "https://api.soundcloud.com/search?&q=test",
        "tx_id": ""
        }
        """
        response = mock.Mock(text=json)
        results = soundcloud.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'http://soundcloud.com/this.is.the.url')
        self.assertEqual(results[0]['content'], 'This is the content')
        self.assertIn(quote_plus('https://api.soundcloud.com/tracks/159723640'), results[0]['embedded'])

        json = """
        {
        "collection": [
            {
            "kind": "user",
            "id": 159723640,
            "created_at": "2014/07/22 00:51:21 +0000",
            "user_id": 2976616,
            "duration": 303780,
            "commentable": true,
            "state": "finished",
            "original_content_size": 13236349,
            "last_modified": "2015/01/31 15:14:50 +0000",
            "sharing": "public",
            "tag_list": "seekae flume",
            "permalink": "seekae-test-recognise-flume-re-work",
            "streamable": true,
            "embeddable_by": "all",
            "downloadable": true,
            "purchase_url": "http://www.facebook.com/seekaemusic",
            "label_id": null,
            "purchase_title": "Seekae",
            "genre": "freedownload",
            "title": "This is the title",
            "description": "This is the content",
            "label_name": "Future Classic",
            "release": "",
            "track_type": "remix",
            "key_signature": "",
            "isrc": "",
            "video_url": null,
            "bpm": null,
            "release_year": 2014,
            "release_month": 7,
            "release_day": 22,
            "original_format": "mp3",
            "license": "all-rights-reserved",
            "uri": "https://api.soundcloud.com/tracks/159723640",
            "user": {
                "id": 2976616,
                "kind": "user",
                "permalink": "flume",
                "username": "Flume",
                "last_modified": "2014/11/24 19:21:29 +0000",
                "uri": "https://api.soundcloud.com/users/2976616",
                "permalink_url": "http://soundcloud.com/flume",
                "avatar_url": "https://i1.sndcdn.com/avatars-000044475439-4zi7ii-large.jpg"
            },
            "permalink_url": "http://soundcloud.com/this.is.the.url",
            "artwork_url": "https://i1.sndcdn.com/artworks-000085857162-xdxy5c-large.jpg",
            "waveform_url": "https://w1.sndcdn.com/DWrL1lAN8BkP_m.png",
            "stream_url": "https://api.soundcloud.com/tracks/159723640/stream",
            "download_url": "https://api.soundcloud.com/tracks/159723640/download",
            "playback_count": 2190687,
            "download_count": 54856,
            "favoritings_count": 49061,
            "comment_count": 826,
            "likes_count": 49061,
            "reposts_count": 15910,
            "attachments_uri": "https://api.soundcloud.com/tracks/159723640/attachments",
            "policy": "ALLOW"
            }
        ],
        "total_results": 375750,
        "next_href": "https://api.soundcloud.com/search?&q=test",
        "tx_id": ""
        }
        """
        response = mock.Mock(text=json)
        results = soundcloud.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        json = """
        {
        "collection": [],
        "total_results": 375750,
        "next_href": "https://api.soundcloud.com/search?&q=test",
        "tx_id": ""
        }
        """
        response = mock.Mock(text=json)
        results = soundcloud.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
