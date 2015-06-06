from collections import defaultdict
import mock
from searx.engines import stackoverflow
from searx.testing import SearxTestCase


class TestStackoverflowEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        params = stackoverflow.request(query, dicto)
        self.assertTrue('url' in params)
        self.assertTrue(query in params['url'])
        self.assertTrue('stackoverflow.com' in params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, stackoverflow.response, None)
        self.assertRaises(AttributeError, stackoverflow.response, [])
        self.assertRaises(AttributeError, stackoverflow.response, '')
        self.assertRaises(AttributeError, stackoverflow.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(stackoverflow.response(response), [])

        html = """
        <div class="question-summary search-result" id="answer-id-1783426">
            <div class="statscontainer">
                <div class="statsarrow"></div>
                <div class="stats">
                    <div class="vote">
                        <div class="votes answered">
                            <span class="vote-count-post "><strong>2583</strong></span>
                            <div class="viewcount">votes</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="summary">
                <div class="result-link">
                    <span>
                        <a href="/questions/this.is.the.url"
                            data-searchsession="/questions"
                            title="Checkout remote Git branch">
                            This is the title
                        </a>
                    </span>
                </div>
                <div class="excerpt">
                    This is the content
                </div>
                <div class="tags user-tags t-git t-git-checkout t-remote-branch">
                </div>
                <div class="started fr">
                    answered <span title="2009-11-23 14:26:08Z" class="relativetime">nov 23 '09</span> by
                    <a href="/users/214090/hallski">hallski</a>
                </div>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = stackoverflow.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], 'https://stackoverflow.com/questions/this.is.the.url')
        self.assertEqual(results[0]['content'], 'This is the content')

        html = """
        <div class="statscontainer">
            <div class="statsarrow"></div>
            <div class="stats">
                <div class="vote">
                    <div class="votes answered">
                        <span class="vote-count-post "><strong>2583</strong></span>
                        <div class="viewcount">votes</div>
                    </div>
                </div>
            </div>
        </div>
        <div class="summary">
            <div class="result-link">
                <span>
                    <a href="/questions/this.is.the.url"
                        data-searchsession="/questions"
                        title="Checkout remote Git branch">
                        This is the title
                    </a>
                </span>
            </div>
            <div class="excerpt">
                This is the content
            </div>
            <div class="tags user-tags t-git t-git-checkout t-remote-branch">
            </div>
            <div class="started fr">
                answered <span title="2009-11-23 14:26:08Z" class="relativetime">nov 23 '09</span> by
                <a href="/users/214090/hallski">hallski</a>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = stackoverflow.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
