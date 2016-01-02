# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import wolframalpha_api
from searx.testing import SearxTestCase


class TestWolframAlphaAPIEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        api_key = 'XXXXXX-XXXXXXXXXX'
        dicto = defaultdict(dict)
        dicto['api_key'] = api_key
        params = wolframalpha_api.request(query, dicto)

        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('wolframalpha.com', params['url'])

        self.assertIn('api_key', params)
        self.assertIn(api_key, params['api_key'])

    def test_response(self):
        self.assertRaises(AttributeError, wolframalpha_api.response, None)
        self.assertRaises(AttributeError, wolframalpha_api.response, [])
        self.assertRaises(AttributeError, wolframalpha_api.response, '')
        self.assertRaises(AttributeError, wolframalpha_api.response, '[]')

        xml = '''<?xml version='1.0' encoding='UTF-8'?>
        <queryresult success='false' error='false' />
        '''

        response = mock.Mock(content=xml)
        self.assertEqual(wolframalpha_api.response(response), [])

        xml = """<?xml version='1.0' encoding='UTF-8'?>
        <queryresult success='false'
            error='false'
            numpods='0'
            datatypes=''
            timedout=''
            timedoutpods=''
            timing='0.241'
            parsetiming='0.074'
            parsetimedout='false'
            recalculate=''
            id=''
            host='http://www5a.wolframalpha.com'
            server='56'
            related=''
            version='2.6'>
         <tips count='1'>
          <tip text='Check your spelling, and use English' />
         </tips>
        </queryresult>
        """

        response = mock.Mock(content=xml)
        self.assertEqual(wolframalpha_api.response(response), [])

        xml = """<?xml version='1.0' encoding='UTF-8'?>
        <queryresult success='true'
            error='false'
            numpods='6'
            datatypes=''
            timedout=''
            timedoutpods=''
            timing='0.684'
            parsetiming='0.138'
            parsetimedout='false'
            recalculate=''
            id='MSPa416020a7966dachc463600000f9c66cc21444cfg'
            host='http://www3.wolframalpha.com'
            server='6'
            related='http://www3.wolframalpha.com/api/v2/relatedQueries.jsp?...'
            version='2.6'>
         <pod title='Input'
             scanner='Identity'
             id='Input'
             position='100'
             error='false'
             numsubpods='1'>
          <subpod title=''>
           <plaintext>sqrt(-1)</plaintext>
          </subpod>
         </pod>
         <pod title='Result'
             scanner='Simplification'
             id='Result'
             position='200'
             error='false'
             numsubpods='1'
             primary='true'>
          <subpod title=''>
           <plaintext></plaintext>
          </subpod>
          <states count='1'>
           <state name='Step-by-step solution'
               input='Result__Step-by-step solution' />
          </states>
         </pod>
         <pod title='Polar coordinates'
             scanner='Numeric'
             id='PolarCoordinates'
             position='300'
             error='false'
             numsubpods='1'>
          <subpod title=''>
           <plaintext>r1 (radius), θ90° (angle)</plaintext>
          </subpod>
         </pod>
         <pod title='Position in the complex plane'
             scanner='Numeric'
             id='PositionInTheComplexPlane'
             position='400'
             error='false'
             numsubpods='1'>
          <subpod title=''>
           <plaintext></plaintext>
          </subpod>
         </pod>
         <pod title='All 2nd roots of -1'
             scanner='RootsOfUnity'
             id=''
             position='500'
             error='false'
             numsubpods='2'>
          <subpod title=''>
           <plaintext>  (principal root)</plaintext>
          </subpod>
          <subpod title=''>
           <plaintext>-</plaintext>
          </subpod>
         </pod>
         <pod title='Plot of all roots in the complex plane'
             scanner='RootsOfUnity'
             id='PlotOfAllRootsInTheComplexPlane'
             position='600'
             error='false'
             numsubpods='1'>
          <subpod title=''>
           <plaintext></plaintext>
          </subpod>
         </pod>
        </queryresult>
        """
        response = mock.Mock(content=xml)
        results = wolframalpha_api.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertIn("i", results[0]['answer'])
        # self.assertIn("sqrt(-1) - Wolfram|Alpha", results[1]['title'])
        # self.assertIn("http://www.wolframalpha.com/input/?i=sqrt%28-1%29", results[1]['url'])

        xml = """<?xml version='1.0' encoding='UTF-8'?>
            <queryresult success='true'
                error='false'
                numpods='2'
                datatypes=''
                timedout=''
                timedoutpods=''
                timing='1.286'
                parsetiming='0.255'
                parsetimedout='false'
                recalculate=''
                id='MSPa195222ad740ede5214h30000480ca61h003d3gd6'
                host='http://www3.wolframalpha.com'
                server='20'
                related='http://www3.wolframalpha.com/api/v2/relatedQueries.jsp?id=...'
                version='2.6'>
             <pod title='Indefinite integral'
                 scanner='Integral'
                 id='IndefiniteIntegral'
                 position='100'
                 error='false'
                 numsubpods='1'
                 primary='true'>
              <subpod title=''>
               <plaintext>∫1/xxlog(x)+constant</plaintext>
              </subpod>
              <states count='1'>
               <state name='Step-by-step solution'
                   input='IndefiniteIntegral__Step-by-step solution' />
              </states>
              <infos count='1'>
               <info text='log(x) is the natural logarithm'>
                <link url='http://reference.wolfram.com/mathematica/ref/Log.html'
                    text='Documentation'
                    title='Mathematica' />
                <link url='http://functions.wolfram.com/ElementaryFunctions/Log'
                    text='Properties'
                    title='Wolfram Functions Site' />
                <link url='http://mathworld.wolfram.com/NaturalLogarithm.html'
                    text='Definition'
                    title='MathWorld' />
               </info>
              </infos>
             </pod>
             <pod title='Plots of the integral'
                 scanner='Integral'
                 id='Plot'
                 position='200'
                 error='false'
                 numsubpods='2'>
              <subpod title=''>
               <plaintext></plaintext>
               <states count='1'>
                <statelist count='2'
                    value='Complex-valued plot'
                    delimiters=''>
                 <state name='Complex-valued plot'
                     input='Plot__1_Complex-valued plot' />
                 <state name='Real-valued plot'
                     input='Plot__1_Real-valued plot' />
                </statelist>
               </states>
              </subpod>
              <subpod title=''>
               <plaintext></plaintext>
               <states count='1'>
                <statelist count='2'
                    value='Complex-valued plot'
                    delimiters=''>
                 <state name='Complex-valued plot'
                     input='Plot__2_Complex-valued plot' />
                 <state name='Real-valued plot'
                     input='Plot__2_Real-valued plot' />
                </statelist>
               </states>
              </subpod>
             </pod>
             <assumptions count='1'>
              <assumption type='Clash'
                  word='integral'
                  template='Assuming &quot;${word}&quot; is ${desc1}. Use as ${desc2} instead'
                  count='2'>
               <value name='IntegralsWord'
                   desc='an integral'
                   input='*C.integral-_*IntegralsWord-' />
               <value name='MathematicalFunctionIdentityPropertyClass'
                   desc='a function property'
                   input='*C.integral-_*MathematicalFunctionIdentityPropertyClass-' />
              </assumption>
             </assumptions>
            </queryresult>
        """
        response = mock.Mock(content=xml)
        results = wolframalpha_api.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertIn("log(x)+c", results[0]['answer'])
        # self.assertIn("integral 1/x - Wolfram|Alpha", results[1]['title'])
        # self.assertIn("http://www.wolframalpha.com/input/?i=integral+1%2Fx", results[1]['url'])
