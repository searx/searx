#!/usr/bin/env python

'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2013- by Adam Tauber, <asciimoo@gmail.com>
'''

if __name__ == "__main__":
    from sys import path
    from os.path import realpath, dirname
    path.append(realpath(dirname(realpath(__file__))+'/../'))

from flask import Flask, request, flash, render_template
import ConfigParser
from os import getenv
from searx.engines import engines
import grequests

cfg = ConfigParser.SafeConfigParser()
cfg.read('/etc/searx.conf')
cfg.read(getenv('HOME')+'/.searxrc')
cfg.read(getenv('HOME')+'/.config/searx/searx.conf')
cfg.read('searx.conf')


app = Flask(__name__)
app.secret_key = cfg.get('app', 'secret_key')

def default_request_params():
    return {'method': 'GET', 'headers': {}, 'data': {}, 'url': ''}

def make_callback(results, callback):
    def process_callback(response, **kwargs):
        results.extend(callback(response))
    return process_callback

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method=='POST':
        if not request.form.get('q'):
            flash('Wrong post data')
            return render_template('index.html')
        query = request.form['q']
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
        return render_template('results.html', results=results, q=query)


    return render_template('index.html')

if __name__ == "__main__":
    from gevent import monkey
    monkey.patch_all()

    app.run(debug        = cfg.get('server', 'debug')
           ,use_debugger = cfg.get('server', 'debug')
           ,port         = int(cfg.get('server', 'port'))
           )
