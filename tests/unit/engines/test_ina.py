from collections import defaultdict
import mock
from searx.engines import ina
from searx.testing import SearxTestCase


class TestInaEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = ina.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('ina.fr' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, ina.response, None)
        self.assertRaises(AttributeError, ina.response, [])
        self.assertRaises(AttributeError, ina.response, '')
        self.assertRaises(AttributeError, ina.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(ina.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(ina.response(response), [])

        json = """
        {"content":"\\t<div class=\\"container\\">\\n\\t\\n\
        <!-- DEBUT CONTENU PRINCIPAL -->\\n<div class=\\"row\\">\\n\
        <div class=\\"search-results--list\\"><div class=\\"media\\">\\n\
        \\t\\t\\t\\t<a class=\\"media-left  media-video  premium    xiti_click_action\\" \
        data-xiti-params=\\"recherche_v4::resultats_conference_de_presse_du_general_de_gaulle::N\\" \
        href=\\"\\/video\\/CAF89035682\\/conference-de-presse-du-general-de-gaulle-video.html\\">\\n\
        <img src=\\"https:\\/\\/www.ina.fr\\/images_v2\\/140x105\\/CAF89035682.jpeg\\" \
        alt=\\"Conf\\u00e9rence de presse du G\\u00e9n\\u00e9ral de Gaulle \\">\\n\
        \\t\\t\\t\\t\\t<\\/a>\\n\
        \\t\\t\\t\\t\\t<div class=\\"media-body\\">\\n\\t\\t\\t\\t\\t\\t<h3 class=\\"h3--title media-heading\\">\\n\
        \\t\\t\\t\\t\\t\\t\\t<a class=\\"xiti_click_action\\" \
        data-xiti-params=\\"recherche_v4::resultats_conference_de_presse_du_general_de_gaulle::N\\" \
        href=\\"\\/video\\/CAF89035682\\/conference-de-presse-du-general-de-gaulle-video.html\\">\
        Conf\\u00e9rence de presse du G\\u00e9n\\u00e9ral de Gaulle <\\/a>\\n\
        <\\/h3>\\n\
        <div class=\\"media-body__info\\">\\n<span class=\\"broadcast\\">27\\/11\\/1967<\\/span>\\n\
        <span class=\\"views\\">29321 vues<\\/span>\\n\
        <span class=\\"duration\\">01h 33m 07s<\\/span>\\n\
        <\\/div>\\n\
        <p class=\\"media-body__summary\\">VERSION INTEGRALE DE LA CONFERENCE DE PRESSE DU GENERAL DE GAULLE . \
              - PA le Pr\\u00e9sident DE GAULLE : il ouvre les bras et s'assied. DP journalis...<\\/p>\\n\
        <\\/div>\\n<\\/div><!-- \\/.media -->\\n"
        }
        """
        response = mock.Mock(text=json)
        results = ina.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], u'Conf\xe9rence de presse du G\xe9n\xe9ral de Gaulle')
        self.assertEqual(results[0]['url'],
                         'https://www.ina.fr/video/CAF89035682/conference-de-presse-du-general-de-gaulle-video.html')
        self.assertEqual(results[0]['content'],
                         u"VERSION INTEGRALE DE LA CONFERENCE DE PRESSE DU GENERAL DE GAULLE ."
                         u" - PA le Pr\u00e9sident DE GAULLE : il ouvre les bras et s'assied. DP journalis...")
