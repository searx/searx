from collections import defaultdict
import mock
from searx.engines import digg
from searx.testing import SearxTestCase


class TestDiggEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = digg.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('digg.com', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, digg.response, None)
        self.assertRaises(AttributeError, digg.response, [])
        self.assertRaises(AttributeError, digg.response, '')
        self.assertRaises(AttributeError, digg.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(digg.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(digg.response(response), [])

        json = """
        {
        "status": "ok",
        "num": 10,
        "next_position": 20,
        "html": "<article itemscope itemtype=\\"http://schema.org/Article\\"
        class=\\"story-container digg-story-el hentry entry story-1sRANah col-1\\"
        data-content-id=\\"1sRANah\\" data-contenturl=\\"http://url.of.link\\"
        data-position=\\"0\\" data-diggs=\\"24\\" data-tweets=\\"69\\"
        data-digg-score=\\"1190\\"> <div class=\\"story-image story-image-thumb\\">
        <a data-position=\\"0\\" data-content-id=\\"1sRANah\\"
        class=\\"story-link\\" href=\\"http://www.thedailybeast.com/\\"
        target=\\"_blank\\"><img class=\\"story-image-img\\"
        src=\\"http://url.of.image.jpeg\\" width=\\"312\\" height=\\"170\\"
        alt=\\"\\" /> </a> </div> <div class=\\"story-content\\"><header
        class=\\"story-header\\"> <div itemprop=\\"alternativeHeadline\\"
        class=\\"story-kicker\\" >Kicker</div> <h2 itemprop=\\"headline\\"
        class=\\"story-title entry-title\\"><a class=\\"story-title-link story-link\\"
        rel=\\"bookmark\\" itemprop=\\"url\\" href=\\"http://www.thedailybeast.com/\\"
        target=\\"_blank\\">Title of article</h2> <div class=\\"story-meta\\">
        <div class=\\"story-score \\">
        <div class=\\"story-score-diggscore diggscore-1sRANah\\">1190</div>
        <div class=\\"story-score-details\\"> <div class=\\"arrow\\"></div>
        <ul class=\\"story-score-details-list\\"> <li
        class=\\"story-score-detail story-score-diggs\\"><span
        class=\\"label\\">Diggs:</span> <span class=\\"count diggs-1sRANah\\">24</span>
        </li> <li class=\\"story-score-detail story-score-twitter\\"><span
        class=\\"label\\">Tweets:</span> <span class=\\"count tweets-1sRANah\\">69</span>
        </li> <li class=\\"story-score-detail story-score-facebook\\"><span
        class=\\"label\\">Facebook Shares:</span> <span
        class=\\"count fb_shares-1sRANah\\">1097</span></li> </ul> </div> </div>
        <span class=\\"story-meta-item story-source\\"> <a
        itemprop=\\"publisher copyrightHolder sourceOrganization provider\\"
        class=\\"story-meta-item-link story-source-link\\"
        href=\\"/source/thedailybeast.com\\">The Daily Beast </a> </span>
        <span class=\\"story-meta-item story-tag first-tag\\"> <a
        itemprop=\\"keywords\\" rel=\\"tag\\"
        class=\\"story-meta-item-link story-tag-link\\" href=\\"/tag/news\\">News</a>
        </span> <abbr class=\\"published story-meta-item story-timestamp\\"
        title=\\"2014-10-18 14:53:45\\"> <time datetime=\\"2014-10-18 14:53:45\\">18 Oct 2014</time>
        </abbr> </div> </header> </div> <ul class=\\"story-actions\\"> <li
        class=\\"story-action story-action-digg btn-story-action-container\\">
        <a class=\\"target digg-1sRANah\\" href=\\"#\\">Digg</a></li> <li
        class=\\"story-action story-action-save btn-story-action-container\\">
        <a class=\\"target save-1sRANah\\" href=\\"#\\">Save</a></li> <li
        class=\\"story-action story-action-share\\"><a
        class=\\"target share-facebook\\" href=\\"https://www.facebook.com/\\">Facebook</a></li>
        <li class=\\"story-action story-action-share\\"><a class=\\"target share-twitter\\"
        href=\\"https://twitter.com/\\">Twitter</a></li> </ul> </article>"
        }
        """
        json = json.replace('\r\n', '').replace('\n', '').replace('\r', '')
        response = mock.Mock(text=json)
        results = digg.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Title of article')
        self.assertEqual(results[0]['url'], 'http://url.of.link')
        self.assertEqual(results[0]['thumbnail'], 'http://url.of.image.jpeg')
        self.assertEqual(results[0]['content'], '')

        json = """
        {
        "status": "error",
        "num": 10,
        "next_position": 20
        }
        """
        response = mock.Mock(text=json)
        results = digg.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
