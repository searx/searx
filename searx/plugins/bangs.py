import json
from os.path import join
from searx.utils import get_external_bang_operator
from flask import redirect, render_template, jsonify
from searx import searx_dir

# https://asciimoo.github.io/searx/dev/plugins.html

# bangs data coming from convert to json with (https://pseitz.github.io/toml-to-json-online-converter/)
# https://raw.githubusercontent.com/jivesearch/jivesearch/master/bangs/bangs.toml

default_on = False


# Plugin info
name = 'Bangs redirect'
description = 'This plugin implements bangs but shows the results directly on the page.'


def pre_search(request, search):
    """
    Redirects if the user supplied a correct bang search.
    :param search: This is a search_query object which contains preferences and the submitted queries.
    :param request: The flask request object.
    :return:
    """

    query = search.search_query
    if query.external_bang:
        search_query = str(query.query, "utf-8")
        bang = get_bang(search_query)
        if bang:
            # TODO add region support.
            bang_url = bang["regions"]["default"]

            search.result_container.redirect_url = bang_url.replace(
                "{{{term}}}",
                get_bang_query(search_query)
            )
    return search.result_container.redirect_url is None


def get_bang(raw_search_query):
    """
    Searches if the supplied user bang is available. Returns None if not found.
    :param raw_search_query: The search query the user providied
    :return: Returns a dict with bangs data (check bangs_data.json for the structure)
    """
    user_bang = get_bang_from_query(raw_search_query)
    try:
        return _get_bangs_data()[user_bang]
    except KeyError:
        return None


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


def get_bang_from_query(raw_query):
    """
    Extracts the bang from a search query.
    :param raw_query: The raw user query coming from the browser
    :return: If the raw_query is &yt yes yes. It returns yt.
    """
    try:
        bang = raw_query.split(" ")[0]
        return bang.replace(get_external_bang_operator(), "")
    except Exception:
        return ""


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
            bangs_data = dict()
            bangs = json.load(json_file)['bang']
            for bang in bangs:
                original_bang = bang.copy()
                # delete trigger because unnecessary data
                del bang["triggers"]

                bang_without_triggers = bang.copy()
                for trigger in original_bang["triggers"]:
                    bangs_data[trigger] = bang_without_triggers

    return bangs_data
