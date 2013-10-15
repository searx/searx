
from os.path import realpath, dirname, splitext, join
from os import listdir
from imp import load_source
import grequests

engine_dir = dirname(realpath(__file__))

engines = []

for filename in listdir(engine_dir):
    modname = splitext(filename)[0]
    if filename.startswith('_') or not filename.endswith('.py'):
        continue
    filepath = join(engine_dir, filename)
    engine = load_source(modname, filepath)
    if not hasattr(engine, 'request') or not hasattr(engine, 'response'):
        continue
    engines.append(engine)

def default_request_params():
    return {'method': 'GET', 'headers': {}, 'data': {}, 'url': ''}

def make_callback(results, callback):
    def process_callback(response, **kwargs):
        results.extend(callback(response))
    return process_callback

def search(query, request):
    global engines
    requests = []
    results = []
    user_agent = request.headers.get('User-Agent', '')
    for engine in engines:
        headers = default_request_params()
        headers['User-Agent'] = user_agent
        request_params = engine.request(query, headers)
        callback = make_callback(results, engine.response)
        if request_params['method'] == 'GET':
            req = grequests.get(request_params['url']
                                ,headers=headers
                                ,hooks=dict(response=callback)
                                )
        else:
            req = grequests.post(request_params['url']
                                ,data=request_params['data']
                                ,headers=headers
                                ,hooks=dict(response=callback)
                                )
        requests.append(req)
    grequests.map(requests)
    return results
