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
                timing='0.826'
                parsetiming='0.17'
                parsetimedout='false'
                recalculate=''
                id='MSPa9721hfe10fii5idac02000029c3a6f09608410h'
                host='http://www4c.wolframalpha.com'
                server='53'
                related='http://www4c.wolframalpha.com/api/v2/relatedQueries.jsp?id=MSPa9731h927ig0h6b1&amp;s=53'
                version='2.6'>
             <pod title='Input'
                 scanner='Identity'
                 id='Input'
                 position='100'
                 error='false'
                 numsubpods='1'>
              <subpod title=''>
               <img src='http://www4c.wolframalpha.com/Calculate/MSP/MSP974111ig68hc?MSPStoreType=image/gif&amp;s=53'
                   alt='sqrt(-1)'
                   title='sqrt(-1)'
                   width='36'
                   height='20' />
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
               <img src='http://www4c.wolframalpha.com/Calculate/MSP/MSP9751hfe101fc27?MSPStoreType=image/gif&amp;s=53'
                   alt='i'
                   title='i'
                   width='5'
                   height='18' />
               <plaintext>i</plaintext>
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
               <img src='http://www4c.wolframalpha.com/Calculate/MSP/MSP97600003i83?MSPStoreType=image/gif&amp;s=53'
                   alt='r = 1 (radius), theta = 90° (angle)'
                   title='r = 1 (radius), theta = 90° (angle)'
                   width='209'
                   height='18' />
               <plaintext>r = 1 (radius), theta = 90° (angle)</plaintext>
              </subpod>
             </pod>
             <pod title='Position in the complex plane'
                 scanner='Numeric'
                 id='PositionInTheComplexPlane'
                 position='400'
                 error='false'
                 numsubpods='1'>
              <subpod title=''>
               <img src='http://www4c.wolframalpha.com/Calculate/MSP/MSP9771e10ficg4g?MSPStoreType=image/gif&amp;s=53'
                   alt=''
                   title=''
                   width='200'
                   height='185' />
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
               <img src='http://www4c.wolframalpha.com/Calculate/MSP/MSP9781hfe10fii?MSPStoreType=image/gif&amp;s=53'
                   alt='i  (principal root)'
                   title='i  (principal root)'
                   width='94'
                   height='18' />
               <plaintext>i  (principal root)</plaintext>
              </subpod>
              <subpod title=''>
               <img src='http://www4c.wolframalpha.com/Calculate/MSP/MSP9791hfe16f2eh1?MSPStoreType=image/gif&amp;s=53'
                   alt='-i'
                   title='-i'
                   width='16'
                   height='18' />
               <plaintext>-i</plaintext>
              </subpod>
             </pod>
             <pod title='Plot of all roots in the complex plane'
                 scanner='RootsOfUnity'
                 id='PlotOfAllRootsInTheComplexPlane'
                 position='600'
                 error='false'
                 numsubpods='1'>
              <subpod title=''>
               <img src='http://www4c.wolframalpha.com/Calculate/MSP/MSP9801h0fi192f9?MSPStoreType=image/gif&amp;s=53'
                   alt=''
                   title=''
                   width='200'
                   height='185' />
               <plaintext></plaintext>
              </subpod>
             </pod>
            </queryresult>
        """
        response = mock.Mock(content=xml)
        results = wolframalpha_api.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertIn("i", results[0]['answer'])

        xml = """<?xml version='1.0' encoding='UTF-8'?>
        <queryresult success='true'
            error='false'
            numpods='2'
            datatypes=''
            timedout='Integral'
            timedoutpods=''
            timing='1.245'
            parsetiming='0.194'
            parsetimedout='false'
            recalculate='http://www4b.wolframalpha.com/api/v2/recalc.jsp?id=MSPa77651gf1a1hie0ii051ea0e1c&amp;s=3'
            id='MSPa77661gf1a1hie5c9d9a600003baifafc1211daef'
            host='http://www4b.wolframalpha.com'
            server='3'
            related='http://www4b.wolframalpha.com/api/v2/relatedQueries.jsp?id=MSPa77671gf1a1hie5c5hc2&amp;s=3'
            version='2.6'>
         <pod title='Indefinite integral'
             scanner='Integral'
             id='IndefiniteIntegral'
             position='100'
             error='false'
             numsubpods='1'
             primary='true'>
          <subpod title=''>
           <img src='http://www4b.wolframalpha.com/Calculate/MSP/MSP776814b9492i9a7gb16?MSPStoreType=image/gif&amp;s=3'
               alt=' integral 1/x dx = log(x)+constant'
               title=' integral 1/x dx = log(x)+constant'
               width='182'
               height='36' />
           <plaintext> integral 1/x dx = log(x)+constant</plaintext>
          </subpod>
          <states count='1'>
           <state name='Step-by-step solution'
               input='IndefiniteIntegral__Step-by-step solution' />
          </states>
          <infos count='1'>
           <info text='log(x) is the natural logarithm'>
            <img src='http://www4b.wolframalpha.com/Calculate/MSP/MSP77691g23eg440g89db?MSPStoreType=image/gif&amp;s=3'
                alt='log(x) is the natural logarithm'
                title='log(x) is the natural logarithm'
                width='198'
                height='18' />
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
           <img src='http://www4b.wolframalpha.com/Calculate/MSP/MSP77701gf1a9d2eb630g9?MSPStoreType=image/gif&amp;s=3'
               alt=''
               title=''
               width='334'
               height='128' />
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
           <img src='http://www4b.wolframalpha.com/Calculate/MSP/MSP77711gf1ai29a34b0ab?MSPStoreType=image/gif&amp;s=3'
               alt=''
               title=''
               width='334'
               height='133' />
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
        </queryresult>
        """
        response = mock.Mock(content=xml)
        results = wolframalpha_api.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertIn("log(x)+c", results[0]['answer'])
