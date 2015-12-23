from collections import defaultdict
import mock
from searx.engines import gigablast
from searx.testing import SearxTestCase


class TestGigablastEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['language'] = 'all'
        params = gigablast.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('gigablast.com' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, gigablast.response, None)
        self.assertRaises(AttributeError, gigablast.response, [])
        self.assertRaises(AttributeError, gigablast.response, '')
        self.assertRaises(AttributeError, gigablast.response, '[]')

        response = mock.Mock(content='<response></response>')
        self.assertEqual(gigablast.response(response), [])

        response = mock.Mock(content='<response></response>')
        self.assertEqual(gigablast.response(response), [])

        xml = """<?xml version="1.0" encoding="UTF-8" ?>
        <response>
            <hits>5941888</hits>
            <moreResultsFollow>1</moreResultsFollow>
            <result>
                <title><![CDATA[This should be the title]]></title>
                <sum><![CDATA[This should be the content.]]></sum>
                <url><![CDATA[http://this.should.be.the.link/]]></url>
                <size>90.5</size>
                <docId>145414002633</docId>
                <siteId>2660021087</siteId>
                <domainId>2660021087</domainId>
                <spidered>1320519373</spidered>
                <indexed>1320519373</indexed>
                <pubdate>4294967295</pubdate>
                <isModDate>0</isModDate>
                <language><![CDATA[English]]></language>
                <charset><![CDATA[UTF-8]]></charset>
            </result>
        </response>
        """
        response = mock.Mock(content=xml)
        results = gigablast.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This should be the title')
        self.assertEqual(results[0]['url'], 'http://this.should.be.the.link/')
        self.assertEqual(results[0]['content'], 'This should be the content.')
