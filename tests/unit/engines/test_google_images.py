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
        dicto['time_range'] = ''
        params = google_images.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])

        dicto['safesearch'] = 0
        params = google_images.request(query, dicto)
        self.assertNotIn('safe', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, google_images.response, None)
        self.assertRaises(AttributeError, google_images.response, [])
        self.assertRaises(AttributeError, google_images.response, '')
        self.assertRaises(AttributeError, google_images.response, '[]')

        html = r"""
["rg_s",["dom","\u003Cstyle\u003E.rg_kn,.rg_s{}.rg_bx{display:-moz-inline-box;display:inline-block;margin-top:0;margin-right:12px;margin-bottom:12px;margin-left:0;overflow:hidden;position:relative;vertical-align:top;z-index:1}.rg_meta{display:none}.rg_l{display:inline-block;height:100%;position:absolute;text-decoration:none;width:100%}.rg_l:focus{outline:0}.rg_i{border:0;color:rgba(0,0,0,0);display:block;-webkit-touch-callout:none;}.rg_an,.rg_anbg,.rg_ilm,.rg_ilmbg{right:0;bottom:0;box-sizing:border-box;-moz-box-sizing:border-box;color:#fff;font:normal 11px arial,sans-serif;line-height:100%;white-space:nowrap;width:100%}.rg_anbg,.rg_ilmbg{background:rgba(51,51,51,0.8);margin-left:0;padding:2px 4px;position:absolute}.rg_ilmn{bottom:0;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.rg_ilm{display:none}#rg_s.rg_kn .rg_l:focus .rg_ilm{display:block}.rg_kn .rg_bx:hover .rg_ilm,.rg_bx:hover .rg_anbg{display:none}.rg_bx:hover .rg_ilm,.rg_anbg,.rg_kn .rg_bx:hover .rg_anbg{display:block}\u003C\/style\u003E\u003Cdiv eid=\"qlKuV-T3BoqksAHMnaroAw\" id=\"isr_scm_0\" style=\"display:none\"\u003E\u003C\/div\u003E\u003Cdiv data-cei=\"qlKuV-T3BoqksAHMnaroAw\" class=\"rg_add_chunk\"\u003E\u003C!--m--\u003E\u003Cdiv class=\"rg_di rg_bx rg_el ivg-i\" data-ved=\"0ahUKEwjk9PCm-7zOAhUKEiwKHcyOCj0QMwgCKAAwAA\"\u003E\u003Ca jsaction=\"fire.ivg_o;mouseover:str.hmov;mouseout:str.hmou\" class=\"rg_l\" style=\"background:rgb(170,205,240)\"\u003E\u003Cimg data-sz=\"f\" name=\"5eykIeMjmCk7xM:\" src=\"https:\/\/encrypted-tbn0.gstatic.com\/images?q=tbn\" class=\"rg_i rg_ic\" alt=\"Image result for south\" jsaction=\"load:str.tbn\" onload=\"google.aft\u0026\u0026google.aft(this)\"\u003E\u003Cdiv class=\"_aOd rg_ilm\"\u003E\u003Cdiv class=\"rg_ilmbg\"\u003E\u003Cspan class=\"rg_ilmn\"\u003E 566\u0026nbsp;\u0026#215;\u0026nbsp;365 - en.wikipedia.org \u003C\/span\u003E\u003C\/div\u003E\u003C\/div\u003E\u003C\/a\u003E\u003Cdiv class=\"rg_meta\"\u003E{\"id\":\"5eykIeMjmCk7xM:\",\"isu\":\"en.wikipedia.org\",\"itg\":false,\"ity\":\"png\",\"oh\":365,\"ou\":\"https:\/\/upload.wikimedia.org\/wikipedia\/commons\/e\/e4\/Us_south_census.png\",\"ow\":566,\"pt\":\"Southern United States - Wikipedia, the free encyclopedia\",\"rid\":\"cErfE02-v-VcAM\",\"ru\":\"https:\/\/en.wikipedia.org\/wiki\/Southern_United_States\",\"s\":\"The Southern United States as defined by the United States Census Bureau.\",\"sc\":1,\"th\":180,\"tu\":\"https:\/\/encrypted-tbn0.gstatic.com\/images?q\\u003dtbn\",\"tw\":280}\u003C\/div\u003E\u003C\/div\u003E\u003C!--n--\u003E\u003C!--m--\u003E\u003Cdiv class=\"rg_di rg_bx rg_el ivg-i\" data-ved=\"0ahUKEwjk9PCm-7zOAhUKEiwKHcyOCj0QMwgDKAEwAQ\"\u003E\u003Ca jsaction=\"fire.ivg_o;mouseover:str.hmov;mouseout:str.hmou\" class=\"rg_l\" style=\"background:rgb(249,252,249)\"\u003E\u003Cimg data-sz=\"f\" name=\"eRjGCc0cFyVkKM:\" src=\"https:\/\/encrypted-tbn2.gstatic.com\/images?q=tbn:ANd9GcSI7SZlbDwdMCgGXzJkpwgdn9uL41xUJ1IiIcKs0qW43_Yp0EhEsg\" class=\"rg_i rg_ic\" alt=\"Image result for south\" jsaction=\"load:str.tbn\" onload=\"google.aft\u0026\u0026google.aft(this)\"\u003E\u003Cdiv class=\"_aOd rg_ilm\"\u003E\u003Cdiv class=\"rg_ilmbg\"\u003E\u003Cspan class=\"rg_ilmn\"\u003E 2000\u0026nbsp;\u0026#215;\u0026nbsp;1002 - commons.wikimedia.org \u003C\/span\u003E\u003C\/div\u003E\u003C\/div\u003E\u003C\/a\u003E\u003Cdiv class=\"rg_meta\"\u003E{\"id\":\"eRjGCc0cFyVkKM:\",\"isu\":\"commons.wikimedia.org\",\"itg\":false,\"ity\":\"png\",\"oh\":1002,\"ou\":\"https:\/\/upload.wikimedia.org\/wikipedia\/commons\/thumb\/8\/84\/South_plate.svg\/2000px-South_plate.svg.png\",\"ow\":2000,\"pt\":\"File:South plate.svg - Wikimedia Commons\",\"rid\":\"F8TVsT2GBLb6RM\",\"ru\":\"https:\/\/commons.wikimedia.org\/wiki\/File:South_plate.svg\",\"s\":\"This image rendered as PNG in other widths: 200px, 500px, 1000px, 2000px.\",\"sc\":1,\"th\":159,\"tu\":\"https:\/\/encrypted-tbn2.gstatic.com\/images?q\\u003dtbn:ANd9GcSI7SZlbDwdMCgGXzJkpwgdn9uL41xUJ1IiIcKs0qW43_Yp0EhEsg\",\"tw\":317}\u003C\/div\u003E\u003C\/div\u003E\u003C!--n--\u003E\u003C\/div\u003E"]]"""  # noqa
        response = mock.Mock(text=html)
        results = google_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], u'Southern United States - Wikipedia, the free encyclopedia')
        self.assertEqual(results[0]['url'], 'https://en.wikipedia.org/wiki/Southern_United_States')
        self.assertEqual(results[0]['img_src'],
                         'https://upload.wikimedia.org/wikipedia/commons/e/e4/Us_south_census.png')
        self.assertEqual(results[0]['content'],
                         'The Southern United States as defined by the United States Census Bureau.')
        self.assertEqual(results[0]['thumbnail_src'],
                         'https://encrypted-tbn0.gstatic.com/images?q=tbn')
