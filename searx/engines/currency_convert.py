from datetime import datetime

categories = []
url = 'http://finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&s={query}=X'
weight = 100

def request(query, params):
    try:
        # eg.: "X EUR in USD"
        ammount, from_currency, _, to_currency = query.split()
        ammount = float(ammount)
    except:
        # wrong params
        return params

    q = (from_currency+to_currency).upper()
    if not q.isalpha():
        return params

    params['url'] = url.format(query=q)
    params['ammount'] = ammount
    params['from'] = from_currency
    params['to'] = to_currency

    return params


def response(resp):
    global base_url
    results = []
    try:
        _,conversion_rate,_ = resp.text.split(',', 2)
        conversion_rate = float(conversion_rate)
    except:
        return results

    title = '{0} {1} in {2} is {3}'.format(resp.search_params['ammount']
                                          ,resp.search_params['from']
                                          ,resp.search_params['to']
                                          ,resp.search_params['ammount']*conversion_rate
                                          )

    content = '1 {0} is {1} {2}'.format(resp.search_params['from'], conversion_rate, resp.search_params['to'])
    now_date = datetime.now().strftime('%Y%m%d')
    url = 'http://finance.yahoo.com/currency/converter-results/{0}/{1}-{2}-to-{3}.html'
    url = url.format(now_date
                    ,resp.search_params['ammount']
                    ,resp.search_params['from'].lower()
                    ,resp.search_params['to'].lower()
                    )
    results.append({'title': title, 'content': content, 'url': url})

    return results
