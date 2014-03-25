from datetime import datetime
import re

categories = []
url = 'http://finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&s={query}=X'
weight = 100

parser_re = re.compile(r'^\W*(\d+(?:\.\d+)?)\W*([a-z]{3})\W*(?:in)?\W*([a-z]{3})\W*$', re.I)  # noqa


def request(query, params):
    m = parser_re.match(query)
    if not m:
        # wrong query
        return params
    try:
        ammount, from_currency, to_currency = m.groups()
        ammount = float(ammount)
    except:
        # wrong params
        return params

    q = (from_currency + to_currency).upper()

    params['url'] = url.format(query=q)
    params['ammount'] = ammount
    params['from'] = from_currency
    params['to'] = to_currency

    return params


def response(resp):
    global base_url
    results = []
    try:
        _, conversion_rate, _ = resp.text.split(',', 2)
        conversion_rate = float(conversion_rate)
    except:
        return results

    title = '{0} {1} in {2} is {3}'.format(
        resp.search_params['ammount'],
        resp.search_params['from'],
        resp.search_params['to'],
        resp.search_params['ammount'] * conversion_rate
    )

    content = '1 {0} is {1} {2}'.format(resp.search_params['from'],
                                        conversion_rate,
                                        resp.search_params['to'])
    now_date = datetime.now().strftime('%Y%m%d')
    url = 'http://finance.yahoo.com/currency/converter-results/{0}/{1}-{2}-to-{3}.html'  # noqa
    url = url.format(
        now_date,
        resp.search_params['ammount'],
        resp.search_params['from'].lower(),
        resp.search_params['to'].lower()
    )
    results.append({'title': title, 'content': content, 'url': url})

    return results
