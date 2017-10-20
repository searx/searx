#!/usr/bin/env python

"""
 PubMed (Scholar publications)
 @website     https://www.ncbi.nlm.nih.gov/pubmed/
 @provide-api yes (https://www.ncbi.nlm.nih.gov/home/develop/api/)
 @using-api   yes
 @results     XML
 @stable      yes
 @parse       url, title, publishedDate, content
 More info on api: https://www.ncbi.nlm.nih.gov/books/NBK25501/
"""

from lxml import etree
from datetime import datetime
from searx.url_utils import urlencode, urlopen


categories = ['science']

base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'\
           + '?db=pubmed&{query}&retstart={offset}&retmax={hits}'

# engine dependent config
number_of_results = 10
pubmed_url = 'https://www.ncbi.nlm.nih.gov/pubmed/'


def request(query, params):
    # basic search
    offset = (params['pageno'] - 1) * number_of_results

    string_args = dict(query=urlencode({'term': query}),
                       offset=offset,
                       hits=number_of_results)

    params['url'] = base_url.format(**string_args)

    return params


def response(resp):
    results = []

    # First retrieve notice of each result
    pubmed_retrieve_api_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'\
                              + 'db=pubmed&retmode=xml&id={pmids_string}'

    # handle Python2 vs Python3 management of bytes and strings
    try:
        pmids_results = etree.XML(resp.text.encode('utf-8'))
    except AttributeError:
        pmids_results = etree.XML(resp.text)

    pmids = pmids_results.xpath('//eSearchResult/IdList/Id')
    pmids_string = ''

    for item in pmids:
        pmids_string += item.text + ','

    retrieve_notice_args = dict(pmids_string=pmids_string)

    retrieve_url_encoded = pubmed_retrieve_api_url.format(**retrieve_notice_args)

    search_results_xml = urlopen(retrieve_url_encoded).read()
    search_results = etree.XML(search_results_xml).xpath('//PubmedArticleSet/PubmedArticle/MedlineCitation')

    for entry in search_results:
        title = entry.xpath('.//Article/ArticleTitle')[0].text

        pmid = entry.xpath('.//PMID')[0].text
        url = pubmed_url + pmid

        try:
            content = entry.xpath('.//Abstract/AbstractText')[0].text
        except:
            content = 'No abstract is available for this publication.'

        #  If a doi is available, add it to the snipppet
        try:
            doi = entry.xpath('.//ELocationID[@EIdType="doi"]')[0].text
            content = 'DOI: ' + doi + ' Abstract: ' + content
        except:
            pass

        if len(content) > 300:
                    content = content[0:300] + "..."
        # TODO: center snippet on query term

        publishedDate = datetime.strptime(entry.xpath('.//DateCreated/Year')[0].text
                                          + '-' + entry.xpath('.//DateCreated/Month')[0].text
                                          + '-' + entry.xpath('.//DateCreated/Day')[0].text, '%Y-%m-%d')

        res_dict = {'url': url,
                    'title': title,
                    'publishedDate': publishedDate,
                    'content': content}

        results.append(res_dict)

        return results
