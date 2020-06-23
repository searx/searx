import json

# https://asciimoo.github.io/searx/dev/plugins.html

# bangs data coming from convert to json with (https://pseitz.github.io/toml-to-json-online-converter/)
# https://raw.githubusercontent.com/jivesearch/jivesearch/master/bangs/bangs.toml

"""
Instructions

To add the plugin go to __init__.py and at the bottom add
plugins.register(bangs)
"""
# to add a plugin
name = 'Bangs redirect'
description = 'This plugin implements bangs but shows the results directly on the page. A bit like DuckDuckGo'

# TODO change to False
default_on = True
bang_operator = "&"

# TODO remove flow
"""
FLOW
    check if it is a bang with ! (maybe customize)
        search if valid bang
            if valid redirect to result page
        else:
            show results from searx
"""


# TODO checks if redirection is possible via this else just use javascript.
def post_search(request, ctx):
    """
    :param request:
    :param ctx:
    :return:
    """
    search_query = request.form.get('q')

    print(is_valid_bang(search_query))
    if is_valid_bang(search_query):
        available_bangs = search_bangs(search_query)
        if len(available_bangs) > 0:
            # If multiple bangs only select the first one
            bang = available_bangs[0]
            # TODO add region support.
            bang_url = bang["regions"]["default"]
            bang_full_with_user_query = bang_url.replace("{{{term}}}", get_bang_query(search_query))
            # TODO actually redirect
            request.base_url = bang_full_with_user_query

            print(bang_full_with_user_query)
            return True
    return False


def get_bang_from_query(raw_query: str):
    """
    Extracts the bang from a search query.
    :param raw_query: The raw user query coming from the browser
    :return: If the raw_query is &yt yes yes. It returns yt.
    """

    bang = raw_query.split(" ")[0]
    return bang.replace(bang_operator, "")


def get_bang_query(raw_query: str):
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


# TODO refactor in different files and package maybe
def is_valid_bang(raw_search_query: str):
    """
    Check whether the given search query is a bang and if it exists in the json bangs_data/bangs.json file.
    :param raw_search_query: The user his search query
    :return: True if it is a valid bang
    """
    # TODO maybe customize with different options then &
    return raw_search_query[0] == bang_operator


def search_bangs(raw_search_query: str):
    """

    :param raw_search_query: The search query the user providied
    :return: Return a list of dicts with all the bangs data (coming from bangs_data/bangs.json)
    """
    user_bang = get_bang_from_query(raw_search_query)
    # Searches for the bang matching the query
    return list(filter(
        lambda bang: user_bang in bang["triggers"], _get_bangs_data())
    )


# TODO make it static
# Dont use this variable directly but access via _get_bangs_data
bangs_data = None


def _get_bangs_data():
    """
    Retrieves the data from the bangs
    :return:
    """
    global bangs_data

    if not bangs_data:
        with open('searx/plugins/bangs_data/bangs.json') as json_file:
            bangs_data = json.load(json_file)['bang']
    return bangs_data
