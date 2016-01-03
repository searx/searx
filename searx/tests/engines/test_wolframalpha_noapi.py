# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import wolframalpha_noapi
from searx.testing import SearxTestCase


class TestWolframAlphaNoAPIEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        params = wolframalpha_noapi.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('wolframalpha.com', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, wolframalpha_noapi.response, None)
        self.assertRaises(AttributeError, wolframalpha_noapi.response, [])
        self.assertRaises(AttributeError, wolframalpha_noapi.response, '')
        self.assertRaises(AttributeError, wolframalpha_noapi.response, '[]')

        html = """
        <!DOCTYPE html>
            <title> Parangaricutirimícuaro - Wolfram|Alpha</title>
            <meta charset="utf-8" />
            <body>
                <div id="closest">
                    <p class="pfail">Wolfram|Alpha doesn't know how to interpret your input.</p>
                    <div id="dtips">
                        <div class="tip">
                            <span class="tip-title">Tip:&nbsp;</span>
                                Check your spelling, and use English
                            <span class="tip-extra"></span>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """

        response = mock.Mock(text=html)
        self.assertEqual(wolframalpha_noapi.response(response), [])

        html = """
        <!DOCTYPE html>
            <title> sqrt(-1) - Wolfram|Alpha</title>
            <meta charset="utf-8" />
            <body>
                <script type="text/javascript">
                  try {
                    document.domain = "wolframalpha.com";
                    context = parent ? parent : document;
                } catch(e){}
                try {
                    if (typeof(context.$) == "undefined") {
                        context = window;
                    } else {
                        $=context.$;
                    }
                }
                catch(e){ context = window;}

            try {

              if (typeof context.jsonArray.popups.pod_0100 == "undefined" ) {
                context.jsonArray.popups.pod_0100 = [];
              }

    context.jsonArray.popups.pod_0100.push( {"stringified": "sqrt(-1)","mInput": "","mOutput": "", "popLinks": {} });

            } catch(e) { }

            try {

            $("#results #pod_0100:not(iframe #pod_0100)")
            .add("#showsteps #pod_0100:not(iframe #pod_0100)")
            .add(".results-pod #pod_0100:not(iframe #pod_0100)")
                .data("tempFileID", 'MSP44501e0dda34g97a0c8900003i71207d6491ab22')
                .data("podIdentifier", '\x22Input\x22')
                .data("podShortIdentifier", '\x22Input\x22')
                .data("buttonStates", '\x22\x22')
                .data("scanner", '\x22\x22');
            $("#results #pod_0100-popup:not(iframe #pod_0100-popup)")
            .add("#showsteps #pod_0100-popup:not(iframe #pod_0100-popup)")
            .add(".results-pod #pod_0100-popup:not(iframe #pod_0100-popup)")
                    .data("tempFileID", 'MSP44501e0dda34g97a0c8900003i71207d6491ab22')
                    .data("podIdentifier", '\x22Input\x22')
                    .data("podShortIdentifier", '\x22Input\x22')
                    .data("buttonStates", '\x22\x22')
                    .data("scanner", '\x22\x22');

              $("#results #subpod_0100_1")
              .add("#showsteps #subpod_0100_1:not(iframe #subpod_0100_1)")
              .add(".results-pod #subpod_0100_1")
                    .data("tempFileID", "MSP44511e0dda34g97a0c89000059490h319161eea3")
                    .data("cellDataTempFile", "MSP44521e0dda34g97a0c89000011378c50d38ede6h")
                    .data("tempFileServer", "")
                    .data("dataSources", "")
                    .data("sources", "")
                    .data("sharetype", "1")
                    .data("shareable", "false");

            } catch(e){}

            //false

            try {

              if (typeof context.jsonArray.popups.pod_0200 == "undefined" ) {
                context.jsonArray.popups.pod_0200 = [];
              }

              context.jsonArray.popups.pod_0200.push( {"stringified": "i","mInput": "","mOutput": "", "popLinks": {} });

            } catch(e) { }

            try {

            $("#results #pod_0200:not(iframe #pod_0200)")
            .add("#showsteps #pod_0200:not(iframe #pod_0200)")
            .add(".results-pod #pod_0200:not(iframe #pod_0200)")
                .data("tempFileID", 'MSP44541e0dda34g97a0c8900004f449i50fa482fd8')
                .data("podIdentifier", '\x22Result\x22')
                .data("podShortIdentifier", '\x22Result\x22')
                .data("buttonStates", '\x22Result\x22\x20\x2D\x3E\x20\x7BAll,\x20None,\x20None,\x20None,\x20None\x7D')
                .data("scanner", '\x22\x22');
            $("#results #pod_0200-popup:not(iframe #pod_0200-popup)")
            .add("#showsteps #pod_0200-popup:not(iframe #pod_0200-popup)")
            .add(".results-pod #pod_0200-popup:not(iframe #pod_0200-popup)")
                    .data("tempFileID", 'MSP44541e0dda34g97a0c8900004f449i50fa482fd8')
                    .data("podIdentifier", '\x22Result\x22')
                    .data("podShortIdentifier", '\x22Result\x22')
                    .data("buttonStates", '\x22Result\x22\x20\x2D\x3E\x20\x7BAll,\x20None,\x20None\x7D')
                    .data("scanner", '\x22\x22');

              $("#results #subpod_0200_1")
              .add("#showsteps #subpod_0200_1:not(iframe #subpod_0200_1)")
              .add(".results-pod #subpod_0200_1")
                    .data("tempFileID", "MSP44551e0dda34g97a0c8900003gdgd37faa7272e0")
                    .data("cellDataTempFile", "MSP44561e0dda34g97a0c89000018ea1iae00104g13")
                    .data("tempFileServer", "")
                    .data("dataSources", "")
                    .data("sources", "")
                    .data("sharetype", "1")
                    .data("shareable", "false");
                    } catch(e){}
                </script>
            </body>
        </html>
        """
        response = mock.Mock(text=html)
        results = wolframalpha_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertIn("i", results[0]['answer'])
        self.assertIn("sqrt(-1) - Wolfram|Alpha", results[1]['title'])
        self.assertIn("http://www.wolframalpha.com/input/?i=+sqrt%28-1%29", results[1]['url'])

        html = """
        <!DOCTYPE html>
            <title> integral 1/x - Wolfram|Alpha</title>
            <meta charset="utf-8" />
            <body>
                <script type="text/javascript">
                //true
                  try {
                    document.domain = "wolframalpha.com";
                    context = parent ? parent : document;
                    } catch(e){}
                    try {
                        if (typeof(context.$) == "undefined") {
                            context = window;
                        } else {
                            $=context.$;
                        }
                    }
                    catch(e){ context = window;}

                try {

                  if (typeof context.jsonArray.popups.pod_0100 == "undefined" ) {
                    context.jsonArray.popups.pod_0100 = [];
                  }

                context.jsonArray.popups.pod_0100.push( {"stringified": "integral 1\/x dx = log(x)+constant"});

                } catch(e) { }

                try {

                $("#results #pod_0100:not(iframe #pod_0100)")
                .add("#showsteps #pod_0100:not(iframe #pod_0100)")
                .add(".results-pod #pod_0100:not(iframe #pod_0100)")
                    .data("tempFileID", 'MSP2051if2202e8bg0757100000d119b05egf583d3')
                    .data("podIdentifier", '\x22IndefiniteIntegral\x22')
                    .data("podShortIdentifier", '\x22IndefiniteIntegral\x22')
                    .data("buttonStates", '\x22Indefinite\x20integral\x22\x20\x2D\x3E\x20\x7B\x7D')
                    .data("scanner", '\x22\x22');
                $("#results #pod_0100-popup:not(iframe #pod_0100-popup)")
                .add("#showsteps #pod_0100-popup:not(iframe #pod_0100-popup)")
                .add(".results-pod #pod_0100-popup:not(iframe #pod_0100-popup)")
                        .data("tempFileID", 'MSP2051if2202e8bg0757100000d119b05egf583d3')
                        .data("podIdentifier", '\x22IndefiniteIntegral\x22')
                        .data("podShortIdentifier", '\x22IndefiniteIntegral\x22')
                        .data("buttonStates", '\x22Indefinite\x20integral\x22\x20\x2D\x3E\x20\x7B\x7D')
                        .data("scanner", '\x22\x22');

                  $("#results #subpod_0100_1")
                  .add("#showsteps #subpod_0100_1:not(iframe #subpod_0100_1)")
                  .add(".results-pod #subpod_0100_1")
                        .data("tempFileID", "MSP2071if2202e8bg0757100004dg60f2a4ca8cf73")
                        .data("cellDataTempFile", "MSP2081if2202e8bg0757100001h18329f72fe90fg")
                        .data("tempFileServer", "")
                        .data("dataSources", "")
                        .data("sources", "")
                        .data("sharetype", "1")
                        .data("shareable", "false");

                } catch(e){}

                //false
                try {

                $("#results #pod_0200:not(iframe #pod_0200)")
                .add("#showsteps #pod_0200:not(iframe #pod_0200)")
                .add(".results-pod #pod_0200:not(iframe #pod_0200)")
                    .data("tempFileID", '')
                    .data("podIdentifier", '\x22Plot\x22')
                    .data("podShortIdentifier", '')
                    .data("buttonStates", '')
                    .data("scanner", '\x22\x22');
                $("#results #pod_0200-popup:not(iframe #pod_0200-popup)")
                .add("#showsteps #pod_0200-popup:not(iframe #pod_0200-popup)")
                .add(".results-pod #pod_0200-popup:not(iframe #pod_0200-popup)")
                        .data("tempFileID", '')
                        .data("podIdentifier", '\x22Plot\x22')
                        .data("podShortIdentifier", '')
                        .data("buttonStates", '')
                        .data("scanner", '\x22\x22');

                } catch(e){}
                </script>
            </body>
        </html>
        """
        response = mock.Mock(text=html)
        results = wolframalpha_noapi.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertIn("log(x)+c", results[0]['answer'])
        self.assertIn("integral 1/x - Wolfram|Alpha", results[1]['title'])
        self.assertIn("http://www.wolframalpha.com/input/?i=+integral+1%2Fx", results[1]['url'])
