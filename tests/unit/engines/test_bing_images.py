# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import bing_images
from searx.testing import SearxTestCase


class TestBingImagesEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        dicto['safesearch'] = 1
        params = bing_images.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('bing.com' in params['url'])
        self.assertTrue('SRCHHPGUSR' in params['cookies'])
        self.assertTrue('fr' in params['cookies']['SRCHHPGUSR'])

        dicto['language'] = 'all'
        params = bing_images.request(query, dicto)
        self.assertIn('SRCHHPGUSR', params['cookies'])
        self.assertIn('en', params['cookies']['SRCHHPGUSR'])

    def test_response(self):
        self.assertRaises(AttributeError, bing_images.response, None)
        self.assertRaises(AttributeError, bing_images.response, [])
        self.assertRaises(AttributeError, bing_images.response, '')
        self.assertRaises(AttributeError, bing_images.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(bing_images.response(response), [])

        response = mock.Mock(text='<html></html>')
        self.assertEqual(bing_images.response(response), [])

        html = """
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        """
        html = html.replace('\r\n', '').replace('\n', '').replace('\r', '')
        response = mock.Mock(text=html)
        results = bing_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test Query')
        self.assertEqual(results[0]['url'], 'http://www.page.url/')
        self.assertEqual(results[0]['content'], '')
        self.assertEqual(results[0]['thumbnail_src'], 'https://www.bing.com/th?id=HN.608003696942779811')
        self.assertEqual(results[0]['img_src'], 'http://test.url/Test%20Query.jpg')

        html = """
        <a href="#" ihk="HN.608003696942779811"
            m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
            mid:&quot;59EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
            surl:&quot;http://www.page.url/&quot;,
            imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,oh:&quot;238&quot;,
            tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
            mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
            t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
            <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
            style="height:144px;" width="178" height="144"/>
        </a>
        """
        response = mock.Mock(text=html)
        results = bing_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)

        html = """
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        <div class="dg_u" style="width:178px;height:144px;left:17px;top:0px">
            <a href="#" ihk="HN.608003696942779811"
                m="{ns:&quot;images&quot;,k:&quot;5045&quot;,
mid:&quot;659EB92C317974F34517A1CCAEBEF76A578E08DEE&quot;,
surl:&quot;http://www.page.url/&quot;,imgurl:&quot;http://test.url/Test%20Query.jpg&quot;,
oh:&quot;238&quot;,tft:&quot;0&quot;,oi:&quot;http://www.image.url/Images/Test%20Query.jpg&quot;}"
                mid="59EB92C317974F34517A1CCAEBEF76A578E08DEE" onclick="return false;"
                t1="Test Query" t2="650 x 517 · 31 kB · jpeg" t3="www.short.url" h="ID=images,5045.1">
                <img src="https://tse4.mm.bing.net/th?id=HN.608003696942779811&amp;o=4&amp;pid=1.7"
                style="height:144px;" width="178" height="144"/>
            </a>
        </div>
        """
        html = html.replace('\r\n', '').replace('\n', '').replace('\r', '')
        response = mock.Mock(text=html)
        results = bing_images.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 10)
