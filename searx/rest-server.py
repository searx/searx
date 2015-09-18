#!flask/bin/python
from flask import Flask, jsonify, request, make_response

from searx import settings
from searx.engines import categories, engines

from searx.searchAPI import Search

from searx.version import VERSION_STRING
from searx.languages import language_codes
from searx.plugins import plugins

app = Flask(__name__, static_url_path="/static/themes/ember")


@app.errorhandler(400)
def handle400(error):
    return make_response(jsonify({'name': error.name, 'description': error.description}), 400)


@app.errorhandler(404)
def handle404(error):
    return make_response(jsonify({'name': error.name, 'description': error.description}), 404)


@app.route('/api/v1.0/search', methods=['GET', 'POST'])
def search_task():
    task = dict(query='', selected_categories=['general'], pageno=1, settings=get_default_settings())

    # task['method'] = request.method
    x_forwarded_for = request.headers.getlist("X-Forwarded-For")
    if x_forwarded_for:
        ip = x_forwarded_for[0]
    else:
        ip = request.remote_addr

    user_data = {
        'method': request.method,
        'ip': ip,
        'ua': request.user_agent
    }
    task['user_data'] = user_data

    if 'query' in request.values:
        task['query'] = request.values['query']
    if 'selected_categories' in request.values:
        task['selected_categories'].append(request.values['selected_categories'])
    if 'selected_categories[]' in request.values:
        task['selected_categories'] = request.values.getlist('selected_categories[]')
    if 'pageno' in request.values:
        task['pageno'] = request.values['pageno']
    if 'settings' in request.values:
        task['settings'] = request.values['settings']

    if not task['query']:
        return make_response(jsonify({'error': 'query empty'}), 500)

    if not task['pageno'] or int(task['pageno']) < 1:
        return make_response(jsonify({'error': 'wrong pageno'}), 500)

    try:
        search = Search(task)
    except:
        return make_response(jsonify(dict(error='task ???')), 500)

    if plugins.callAPI('pre_search', task, locals()):
        search.search(task)

    plugins.callAPI('post_search', task, locals())

    return jsonify({'results': search.results,
                    'suggestions': search.suggestions,
                    'answers': search.answers,
                    'infoboxes': search.infoboxes
                    })


@app.route('/api/v1.0/settings', methods=['GET'])
def get_settings():
    return jsonify(get_default_settings())


def get_default_settings():
    engs = []
    langs = []
    plugs = []

    for engine in engines.values():
        eng = {
            'name': engine.name,
            'paging': engine.paging,
            'categories': engine.categories,
            'language_support': engine.language_support,
            'safesearch': engine.safesearch,
            'timeout': engine.timeout,
            'shortcut': engine.shortcut,
            'disabled': engine.disabled
        }
        engs.append(eng)

    for plugin in plugins:
        plug = {
            'name': plugin.name,
            'allow': plugin.default_on,
            'description': plugin.description
        }
        plugs.append(plug)

    for lang_id, lang_name, country_name in language_codes:
        lang = {
            'id': lang_id,
            'name': lang_name,
            'country_name': country_name
        }
        langs.append(lang)

    setting = {'engines': engs,
               'default_locale': get_locale(),
               'locales': settings['locales'],
               'all_categories': sorted(categories.keys()),
               'search': settings['search'],
               'image_proxy': settings['server'].get('image_proxy'),
               'plugins': plugs,
               'languages': langs,
               'version': VERSION_STRING}
    return setting


def get_locale():
    locale = request.accept_languages.best_match(settings['locales'].keys())

    if settings['ui'].get('default_locale'):
        locale = settings['ui']['default_locale']

    if request.cookies.get('locale', '') in settings['locales']:
        locale = request.cookies.get('locale', '')

    if 'locale' in request.args \
            and request.args['locale'] in settings['locales']:
        locale = request.args['locale']

    if 'locale' in request.form \
            and request.form['locale'] in settings['locales']:
        locale = request.form['locale']

    return locale


@app.before_request
def option_autoreply():
    """ Always reply 200 on OPTIONS request """

    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()

        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']

        h = resp.headers

        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        # We also keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers

        return resp


@app.after_request
def set_allow_origin(resp):
    """ Set origin for GET, POST, PUT, DELETE requests """

    h = resp.headers

    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']

    return resp

if __name__ == '__main__':
    app.run(
        debug=settings['general']['debug'],
        use_debugger=settings['general']['debug'],
        port=settings['server']['port'],
        host=settings['server']['bind_address']
    )
