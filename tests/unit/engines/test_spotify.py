from collections import defaultdict
import mock
from searx.engines import spotify
from searx.testing import SearxTestCase


class TestSpotifyEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = spotify.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('spotify.com', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, spotify.response, None)
        self.assertRaises(AttributeError, spotify.response, [])
        self.assertRaises(AttributeError, spotify.response, '')
        self.assertRaises(AttributeError, spotify.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(spotify.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(spotify.response(response), [])

        json = """
        {
          "tracks": {
            "href": "https://api.spotify.com/v1/search?query=nosfell&offset=0&limit=20&type=track",
            "items": [
              {
                "album": {
                  "album_type": "album",
                  "external_urls": {
                    "spotify": "https://open.spotify.com/album/5c9ap1PBkSGLxT3J73toxA"
                  },
                  "href": "https://api.spotify.com/v1/albums/5c9ap1PBkSGLxT3J73toxA",
                  "id": "5c9ap1PBkSGLxT3J73toxA",
                  "name": "Album Title",
                  "type": "album",
                  "uri": "spotify:album:5c9ap1PBkSGLxT3J73toxA"
                },
                "artists": [
                  {
                    "external_urls": {
                      "spotify": "https://open.spotify.com/artist/0bMc6b75FfZEpQHG1jifKu"
                    },
                    "href": "https://api.spotify.com/v1/artists/0bMc6b75FfZEpQHG1jifKu",
                    "id": "0bMc6b75FfZEpQHG1jifKu",
                    "name": "Artist Name",
                    "type": "artist",
                    "uri": "spotify:artist:0bMc6b75FfZEpQHG1jifKu"
                  }
                ],
                "disc_number": 1,
                "duration_ms": 202386,
                "explicit": false,
                "external_ids": {
                  "isrc": "FRV640600067"
                },
                "external_urls": {
                  "spotify": "https://open.spotify.com/track/2GzvFiedqW8hgqUpWcASZa"
                },
                "href": "https://api.spotify.com/v1/tracks/2GzvFiedqW8hgqUpWcASZa",
                "id": "1000",
                "is_playable": true,
                "name": "Title of track",
                "popularity": 6,
                "preview_url": "https://p.scdn.co/mp3-preview/7b8ecda580965a066b768c2647f877e43f7b1a0a",
                "track_number": 3,
                "type": "track",
                "uri": "spotify:track:2GzvFiedqW8hgqUpWcASZa"
              }
            ],
            "limit": 20,
            "next": "https://api.spotify.com/v1/search?query=nosfell&offset=20&limit=20&type=track",
            "offset": 0,
            "previous": null,
            "total": 107
          }
        }
        """
        response = mock.Mock(text=json)
        results = spotify.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title of track')
        self.assertEqual(results[0]['url'], 'https://open.spotify.com/track/2GzvFiedqW8hgqUpWcASZa')
        self.assertEqual(results[0]['content'], 'Artist Name - Album Title - Title of track')
        self.assertIn('1000', results[0]['embedded'])

        json = """
        {
          "tracks": {
            "href": "https://api.spotify.com/v1/search?query=nosfell&offset=0&limit=20&type=track",
            "items": [
              {
                "href": "https://api.spotify.com/v1/tracks/2GzvFiedqW8hgqUpWcASZa",
                "id": "1000",
                "is_playable": true,
                "name": "Title of track",
                "popularity": 6,
                "preview_url": "https://p.scdn.co/mp3-preview/7b8ecda580965a066b768c2647f877e43f7b1a0a",
                "track_number": 3,
                "type": "album",
                "uri": "spotify:track:2GzvFiedqW8hgqUpWcASZa"
              }
            ],
            "limit": 20,
            "next": "https://api.spotify.com/v1/search?query=nosfell&offset=20&limit=20&type=track",
            "offset": 0,
            "previous": null,
            "total": 107
          }
        }
        """
        response = mock.Mock(text=json)
        results = spotify.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
