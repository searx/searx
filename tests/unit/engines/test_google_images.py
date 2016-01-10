from collections import defaultdict
import mock
from searx.engines import google_images
from searx.testing import SearxTestCase


class TestGoogleImagesEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['safesearch'] = 1
        params = google_images.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('safe=active', params['url'])

        dicto['safesearch'] = 0
        params = google_images.request(query, dicto)
        self.assertNotIn('safe', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, google_images.response, None)
        self.assertRaises(AttributeError, google_images.response, [])
        self.assertRaises(AttributeError, google_images.response, '')
        self.assertRaises(AttributeError, google_images.response, '[]')

        response = mock.Mock(text='<div></div>')
        self.assertEqual(google_images.response(response), [])

        html = """
<div style="display:none">
  <div eid="fWhnVq4Shqpp3pWo4AM" id="isr_scm_1" style="display:none"></div>
  <div data-cei="fWhnVq4Shqpp3pWo4AM" class="rg_add_chunk"><!--m-->
    <div class="rg_di rg_el ivg-i" data-ved="0ahUKEwjuxPWQts3JAhUGVRoKHd4KCjwQMwgDKAAwAA">
      <a href="/imgres?imgurl=http://www.clker.com/cliparts/H/X/l/b/0/0/south-arrow-hi.png&amp;imgrefurl=http://www.clker.com/clipart-south-arrow.html&amp;h=598&amp;w=504&amp;tbnid=bQWQ9wz9loJmjM:&amp;docid=vlONkeBtERfDuM&amp;ei=fWhnVq4Shqpp3pWo4AM&amp;tbm=isch" jsaction="fire.ivg_o;mouseover:str.hmov;mouseout:str.hmou" class="rg_l"><img data-src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsxy3gKnEX0lrwwpRxdPWyLJ8iZ--PXZ-ThbBA2_xXDG_bdQutMQ" data-sz="f" name="bQWQ9wz9loJmjM:" class="rg_i" alt="Image result for south" jsaction="load:str.tbn" onload="google.aft&&google.aft(this)">
        <div class="_aOd rg_ilm">
          <div class="rg_ilmbg"><span class="rg_ilmn"> 504&nbsp;&#215;&nbsp;598 - clker.com </span>
          </div>
        </div>
      </a>
      <div class="rg_meta">
        {"id":"bQWQ9wz9loJmjM:","isu":"clker.com","ity":"png","md":"/search?tbs\u003dsbi:AMhZZit7u1mHyop9pQisu-5idR-8W_1Itvwc3afChmsjQYPx_1yYMzBvUZgtkcGoojqekKZ-6n_1rjX9ySH0OWA_1eO5OijFY6BBDw_1GApr6xxb1bXJcBcj-DiguMoXWW7cZSG7MRQbwnI5SoDZNXcv_1xGszy886I7NVb_1oRKSliTHtzqbXAxhvYreM","msu":"/search?q\u003dsouth\u0026biw\u003d1364\u0026bih\u003d235\u0026tbm\u003disch\u0026tbs\u003dsimg:CAQSEgltBZD3DP2WgiG-U42R4G0RFw","oh":598,"os":"13KB","ow":504,"pt":"South Arrow Clip Art at Clker.com - vector clip art online ...","rid":"vlONkeBtERfDuM","s":"Download this image as:","sc":1,"si":"/search?q\u003dsouth\u0026biw\u003d1364\u0026bih\u003d235\u0026tbm\u003disch\u0026tbs\u003dsimg:CAESEgltBZD3DP2WgiG-U42R4G0RFw","th":245,"tu":"https://thumbnail.url/","tw":206}
      </div>
    </div><!--n--><!--m-->
  </div>
</div>
        """  # noqa
        response = mock.Mock(text=html)
        results = google_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], u'South Arrow Clip Art at Clker.com - vector clip art online ...')
        self.assertEqual(results[0]['url'], 'http://www.clker.com/clipart-south-arrow.html')
        self.assertEqual(results[0]['thumbnail_src'], 'https://thumbnail.url/')
        self.assertEqual(results[0]['img_src'], 'http://www.clker.com/cliparts/H/X/l/b/0/0/south-arrow-hi.png')
        self.assertEqual(results[0]['content'], 'Download this image as:')
