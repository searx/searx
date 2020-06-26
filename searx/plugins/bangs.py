import json
from os.path import join

from flask import redirect, render_template, jsonify
from searx import searx_dir

# https://asciimoo.github.io/searx/dev/plugins.html

# bangs data coming from convert to json with (https://pseitz.github.io/toml-to-json-online-converter/)
# https://raw.githubusercontent.com/jivesearch/jivesearch/master/bangs/bangs.toml

"""
Instructions

To add the plugin go to __init__.py and at the bottom add
plugins.register(bangs)
"""


default_on = False
bang_operator = "!"
help_bang_operator = "{}help".format(bang_operator)
show_bangs_operator = "{}bangs".format(bang_operator)


# Plugin info
name = 'Bangs redirect'
description = 'This plugin implements bangs but shows the results directly on the page. ' \
              'Learn more by entering {} on the home page.'.format(help_bang_operator)


def custom_results(search_query_obj, request):
    """
    Redirects if the user supplied a correct bang search.
    :param search_query_obj: Search object which contains preferences and the submitted queries.
    :param request: The flask request object.
    :return: A flask response or None if the plugin did nothing
    """

    # If I import it above I get a circular dependency error.
    from searx.search import get_search_query_from_webapp

    filtered_search_query, raw_search_query = get_search_query_from_webapp(request.preferences, request.form)
    search_query = raw_search_query.query
    if search_query == help_bang_operator:
        return render_help_bangs_page(request)
    if search_query == show_bangs_operator:
        return render_available_bangs(request)
    print(is_valid_bang(search_query))
    if is_valid_bang(search_query):
        available_bangs = search_bangs(search_query)
        if len(available_bangs) > 0:
            # If multiple bangs only select the first one
            bang = available_bangs[0]
            # TODO add region support.
            bang_url = bang["regions"]["default"]
            bang_full_with_user_query = bang_url.replace("{{{term}}}", get_bang_query(search_query))
            print(bang_full_with_user_query)
            return redirect(bang_full_with_user_query)
    return None


def render_available_bangs(request):
    return jsonify(_get_bangs_data())


def render_help_bangs_page(request):
    # TODO add paging
    return render_template(
        "plugins/bangs/help_bangs.html",
        operators=[
            {
                "operator": show_bangs_operator,
                "description": "Shows all the available bangs on a given instance."
            },
            {
                "operator": help_bang_operator,
                "description": "Shows this help/setting page."
            },
        ],
    )


def get_bang_from_query(raw_query):
    """
    Extracts the bang from a search query.
    :param raw_query: The raw user query coming from the browser
    :return: If the raw_query is &yt yes yes. It returns yt.
    """

    bang = raw_query.split(" ")[0]
    return bang.replace(bang_operator, "")


def get_bang_query(raw_query):
    """
    Gets the actual user search.
    :param raw_query: The raw user query coming from the browser
    :return: For example with the query &yt yes yes then this function will return yes yes.
    """
    slitted_raw_query = raw_query.split(" ")

    full_query = ""
    # Cause the first one is the bang like &yt
    for raw_query in slitted_raw_query[1:]:
        full_query += raw_query + "%20"
    return full_query


def is_valid_bang(raw_search_query):
    """
    Check whether the given search query is a bang and if it exists in the json bangs_data/bangs.json file.
    :param raw_search_query: The user his search query in str
    :return: True if it is a valid bang
    """
    print(raw_search_query[0])
    return raw_search_query[0] == bang_operator


def search_bangs(raw_search_query):
    """
    Searches if the bang is available.
    :param raw_search_query: The search query the user providied
    :return: Return a list of dicts with all the bangs data (coming from bangs_data/bangs.json)
    """
    user_bang = get_bang_from_query(raw_search_query)
    # Searches for the bang matching the query
    return list(filter(
        lambda bang: user_bang in bang["triggers"], _get_bangs_data()
    ))


# Dont use this variable directly but access via _get_bangs_data
bangs_data = None


def _get_bangs_data():
    """
    Retrieves the data from the bangs
    :return:
    """
    global bangs_data

    if not bangs_data:
        with open(join(searx_dir, 'plugins/bangs_data/bangs.json')) as json_file:
            bangs_data = json.load(json_file)['bang']
    return bangs_data
