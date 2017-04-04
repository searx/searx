# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import framalibre
from searx.testing import SearxTestCase


class TestFramalibreEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = framalibre.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('framalibre.org' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, framalibre.response, None)
        self.assertRaises(AttributeError, framalibre.response, [])
        self.assertRaises(AttributeError, framalibre.response, '')
        self.assertRaises(AttributeError, framalibre.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(framalibre.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(framalibre.response(response), [])

        html = u"""
        <div class="nodes-list-row">
          <div id="node-431"
              class="node node-logiciel-annuaires node-promoted node-teaser node-teaser node-sheet clearfix nodes-list"
              about="/content/gogs" typeof="sioc:Item foaf:Document">
            <header class="media">
              <div class="media-left">
                <div class="field field-name-field-logo field-type-image field-label-hidden">
                  <div class="field-items">
                    <div class="field-item even">
                      <a href="/content/gogs">
                        <img class="media-object img-responsive" typeof="foaf:Image"
 src="https://framalibre.org/sites/default/files/styles/teaser_logo/public/leslogos/gogs-lg.png?itok=rrCxKKBy"
 width="70" height="70" alt="" />
                      </a>
                    </div>
                  </div>
                </div>
              </div>
              <div class="media-body">
                <h3 class="node-title"><a href="/content/gogs">Gogs</a></h3>
                <span property="dc:title" content="Gogs" class="rdf-meta element-hidden"></span>
                <div class="field field-name-field-annuaires field-type-taxonomy-term-reference field-label-hidden">
                  <div class="field-items">
                    <div class="field-item even">
                      <a href="/annuaires/cloudwebapps"
 typeof="skos:Concept" property="rdfs:label skos:prefLabel"
 datatype="" class="label label-primary">Cloud/webApps</a>
                    </div>
                  </div>
                </div>
              </div>
            </header>
            <div class="content">
              <div class="field field-name-field-votre-appr-ciation field-type-fivestar field-label-hidden">
                <div class="field-items">
                  <div class="field-item even">
                  </div>
                </div>
              </div>
              <div class="field field-name-body field-type-text-with-summary field-label-hidden">
                <div class="field-items">
                  <div class="field-item even" property="content:encoded">
                    <p>Gogs est une interface web basée sur git et une bonne alternative à GitHub.</p>
                  </div>
                </div>
              </div>
            </div>
            <footer>
              <a href="/content/gogs" class="read-more btn btn-default btn-sm">Voir la notice</a>
              <div class="field field-name-field-lien-officiel field-type-link-field field-label-hidden">
                <div class="field-items">
                  <div class="field-item even">
                    <a href="https://gogs.io/" target="_blank" title="Voir le site officiel">
                      <span class="glyphicon glyphicon-globe"></span>
                      <span class="sr-only">Lien officiel</span>
                    </a>
                  </div>
                </div>
              </div>
            </footer>
          </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = framalibre.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Gogs')
        self.assertEqual(results[0]['url'],
                         'https://framalibre.org/content/gogs')
        self.assertEqual(results[0]['content'],
                         u"Gogs est une interface web basée sur git et une bonne alternative à GitHub.")
