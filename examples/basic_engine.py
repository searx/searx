
categories = ['general'] # optional

def request(query, params):
    '''pre-request callback
    params<dict>:
      method  : POST/GET
      headers : {}
      data    : {} # if method == POST
      url     : ''
    '''

    params['url'] = 'https://host/%s' % query

    return params


def response(resp):
    '''post-response callback
    resp: requests response object
    '''
    return [{'url': '', 'title': '', 'content': ''}]

