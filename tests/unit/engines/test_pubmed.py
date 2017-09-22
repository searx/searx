# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import pubmed
from searx.testing import SearxTestCase


class TestPubmedEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = pubmed.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn('eutils.ncbi.nlm.nih.gov/', params['url'])
        self.assertIn('term', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, pubmed.response, None)
        self.assertRaises(AttributeError, pubmed.response, [])
        self.assertRaises(AttributeError, pubmed.response, '')
        self.assertRaises(AttributeError, pubmed.response, '[]')

        response = mock.Mock(text='<PubmedArticleSet></PubmedArticleSet>')
        self.assertEqual(pubmed.response(response), [])

        xml_mock = """<eSearchResult><Count>1</Count><RetMax>1</RetMax><RetStart>0</RetStart><IdList>
<Id>1</Id>
</IdList></eSearchResult>
"""
# The engine retrieves abstracts with a second api call, hence testing indirectly
#         xml_res_mock = """<PubmedArticleSet>
# <PubmedArticle>
#     <MedlineCitation Status="MEDLINE" Owner="NLM">
#         <PMID Version="1">87654321</PMID>
#         <DateCreated>
#             <Year>2000</Year>
#             <Month>01</Month>
#             <Day>01</Day>
#         </DateCreated>
#         <DateCompleted>
#             <Year>2000</Year>
#             <Month>01</Month>
#             <Day>01</Day>
#         </DateCompleted>
#         <DateRevised>
#             <Year>2000</Year>
#             <Month>01</Month>
#             <Day>01</Day>
#         </DateRevised>
#         <Article PubModel="Print-Electronic">
#             <Journal>
#                 <ISSN IssnType="Electronic">1111-1111</ISSN>
#                 <JournalIssue CitedMedium="Internet">
#                     <Volume>01</Volume>
#                     <Issue>1</Issue>
#                     <PubDate>
#                         <Year>2000</Year>
#                         <Month>Jan</Month>
#                     </PubDate>
#                 </JournalIssue>
#                 <Title>Journal of Anything</Title>
#                 <ISOAbbreviation>J. An.</ISOAbbreviation>
#             </Journal>
#             <ArticleTitle>This experiment was something.</ArticleTitle>
#             <Pagination>
#                 <MedlinePgn>111-11</MedlinePgn>
#             </Pagination>
#             <ELocationID EIdType="doi" ValidYN="Y">10.1000/xyz123</ELocationID>
#             <Abstract>
#                 <AbstractText>This experiment was abstract. In fact that was a Gedanken Experiment.</AbstractText>
#             </Abstract>
#             <AuthorList CompleteYN="Y">
#                 <Author ValidYN="Y">
#                     <LastName>Nietsnie</LastName>
#                     <ForeName>Derfla</ForeName>
#                     <Initials>N</Initials>
#                     <AffiliationInfo>
#                         <Affiliation>University of the world.</Affiliation>
#                     </AffiliationInfo>
#                 </Author>
#             </AuthorList>
#             <Language>eng</Language>
#             <PublicationTypeList>
#                 <PublicationType UI="D016428">Journal Article</PublicationType>
#                 <PublicationType UI="D013485">Research Support, Non-U.S. Gov't</PublicationType>
#             </PublicationTypeList>
#             <ArticleDate DateType="Electronic">
#                 <Year>2000</Year>
#                 <Month>01</Month>
#                 <Day>01</Day>
#             </ArticleDate>
#         </Article>
#         <MedlineJournalInfo>
#             <Country>Germany</Country>
#             <MedlineTA>J An</MedlineTA>
#             <NlmUniqueID>87654321</NlmUniqueID>
#             <ISSNLinking>1111-1111</ISSNLinking>
#         </MedlineJournalInfo>
#     </MedlineCitation>
#     <PubmedData>
#         <ArticleIdList>
#             <ArticleId IdType="pubmed">12345678</ArticleId>
#             <ArticleId IdType="doi">10.1000/xyz123</ArticleId>
#         </ArticleIdList>
#     </PubmedData>
# </PubmedArticle>
# </PubmedArticleSet>"""

        response = mock.Mock(text=xml_mock.encode('utf-8'))
        results = pubmed.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], 'No abstract is available for this publication.')
