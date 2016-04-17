from youtube_dl import YoutubeDL
import json


class YoutubeDLParser(object):

    def __init__(self, links):
        self.links = links

    def debug(self, msg):
        # process youtube-dl output one line at a time
        try:
            # try to parse the output as a JSON string
            data = json.loads(msg)
        except ValueError:
            # if parsing fails, it is one of the status strings, we can safely skip it
            return

        formats = data.get('formats', [])
        if len(formats) == 0:
            return []

        fields = {'ext': 'ext',
                  'url': 'url',
                  'name': 'format',
                  'resolution': 'resolution',
                  'note': 'format_note',
                  'ac': 'acodec',
                  'vc': 'vcodec'}

        for fmt in formats:
            info = {}
            for k, v in fields.iteritems():
                info[k] = fmt.get(v, '').strip()
            self.links.append(info)

    def warning(self, msg):
        print 'YoutubeDL WARNING: ' + msg

    def error(self, msg):
        print 'YoutubeDL ERROR: ' + msg


def extract_video_links(url):
    if not url:
        return []

    links = []

    # youtube-dl options
    options = {
        # force JSON output to facilitate parsing
        'forcejson': True,

        # do not download anything, just return the links and information
        'skip_download': True,

        # object used to process youtube-dl output
        'logger': YoutubeDLParser(links)
    }

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([str(url)])
    except Exception as e:
        print 'youtube-dl exception: ' + str(e)

    return links
