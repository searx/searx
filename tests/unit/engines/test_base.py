# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import startpage
from searx.testing import SearxTestCase


class TestBaseEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = base.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn('base-search.net', params['url'])
        self.assertIn('query', params)
        self.assertIn('query', params['query'])
        self.assertIn(query, params['query']['query'])

    def test_response(self):
        self.assertRaises(AttributeError, base.response, None)
        self.assertRaises(AttributeError, base.response, [])
        self.assertRaises(AttributeError, base.response, '')
        self.assertRaises(AttributeError, base.response, '[]')

        response = mock.Mock(text='<response></response>')
        self.assertEqual(base.response(response), [])

        xml_mock = """<?xml version="1.0"?>
<response>
  <lst name="responseHeader">
    <int name="status">0</int>
    <int name="QTime">1</int>
    <lst name="params">
      <str name="q">science</str>
      <str name="fl">dccollection,dccontenttype,dccontinent,dccountry,dccreator,dcdate,dcdescription,dcdocid,dcdoi,dcformat,dcidentifier,dclang,dclanguage,dclink,dcperson,dcpublisher,dcrights,dcsource,dcsubject,dctitle,dcyear,dctype,dcclasscode,dctypenorm,dcdeweyfull,dcdeweyhuns,dcdeweytens,dcdeweyones,dcautoclasscode,dcrelation,dccontributor,dccoverage,dchdate,dcoa,dcrightsnorm</str>
      <str name="fq">-collection:(ftethz OR ftunivcalgary OR ftunivberkeley OR ftunivtampubl OR ftutunomiya OR ftwroclawunivt OR ftlibdiglib OR ftdsto OR ftgaziuniv OR ftkyotoit OR ftiiap OR ftjinsight OR ftscieloperu OR ftnortheastdc OR ftredined OR ftbibnum OR ftunivcadakar OR ftntnormaluniv OR ftehps OR ftdhhs OR ftnunivtre OR fttunghaiuniv OR fthssognogfjorda OR ftiainsunanampel OR ftredecedes OR fthacettepeuniv OR ftunivjos OR ftentscholar OR ftnaviationuniv OR ftstmikjakibbi OR ftfontagro OR ftchinacadsciehf OR fteapzamorano OR ftmlzgarchingvdb OR ftuninlitoralcol OR ftsdunivir OR ftinfsciencesojs OR ftkansaiwomens OR fttohokupuniv OR ftmevlanauniv OR ftjassalam OR ftifmtcfsojs OR ftcovenantuniojs OR ftcasrpojs OR ftjdinja OR ftlebanameruni OR ftunivpahlawantt OR ftjhsap)</str>
      <str name="rows">1</str>
      <str name="bq">oa:1^2</str>
    </lst>
  </lst>
  <result name="response" numFound="1" start="0">
    <doc>
      <date name="dchdate">2000-01-01T01:01:01Z</date>
      <str name="dcdocid">1</str>
      <str name="dccontinent">cna</str>
      <str name="dccountry">us</str>
      <str name="dccollection">ftciteseerx</str>
      <str name="dcprovider">CiteSeerX</str>
      <str name="dctitle">Science and more</str>
      <arr name="dccreator">
        <str>Someone</str>
      </arr>
      <arr name="dcperson">
        <str>Someone</str>
      </arr>
      <arr name="dcsubject">
        <str>Science and more</str>
      </arr>
      <str name="dcdescription">Science, and even more.</str>
      <arr name="dccontributor">
        <str>The neighbour</str>
      </arr>
      <str name="dcdate">2001</str>
      <int name="dcyear">2001</int>
      <arr name="dctype">
        <str>text</str>
      </arr>
      <arr name="dctypenorm">
        <str>1</str>
      </arr>
      <arr name="dcformat">
        <str>application/pdf</str>
      </arr>
      <arr name="dccontenttype">
        <str>application/pdf</str>
      </arr>
      <arr name="dcidentifier">
        <str>http://example.org/</str>
      </arr>
      <str name="dclink">http://example.org</str>
      <str name="dcsource">http://example.org</str>
      <arr name="dclanguage">
        <str>en</str>
      </arr>
      <str name="dcrights">Under the example.org licence</str>
      <int name="dcoa">1</int>
      <arr name="dclang">
        <str>eng</str>
      </arr>
    </doc>
  </result>
</respionse>"""

        response = mock.Mock(text=xml_res.encode('utf-8'))
        results = base.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Science and more')
        self.assertEqual(results[0]['content'], 'Science, and even more.')
