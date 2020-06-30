import json
from os.path import join
from searx import searx_dir

# bangs data coming from the following url convert to json with
# https://raw.githubusercontent.com/jivesearch/jivesearch/master/bangs/bangs.toml
# https://pseitz.github.io/toml-to-json-online-converter/
# NOTE only use the get_bang_url


def get_bang_url(search):
    """
    Redirects if the user supplied a correct bang search.
    :param search: This is a search_query object which contains preferences and the submitted queries.
    :return: None if the bang was invalid, else a string of the redirect url.
    """

    if search.external_bang:
        query = str(search.query, "utf-8")
        bang = _get_bang(search.external_bang)
        if bang:
            # TODO add region support.
            bang_url = bang["regions"]["default"]

            return bang_url.replace("{{{term}}}", _get_bang_query(query))
    return None


def _get_external_bang_operator():
    """
    :return: Returns the external bang operator used in Searx.
    """
    return "!!"


def _get_bang(user_bang):
    """
    Searches if the supplied user bang is available. Returns None if not found.
    :param user_bang: The parsed user bang. For example yt
    :return: Returns a dict with bangs data (check bangs_data.json for the structure)
    """
    try:
        return _get_bangs_data()[user_bang]
    except KeyError:
        return None


def _get_bang_query(raw_query):
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


def _get_bang_from_query(raw_query):
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
        with open(join(searx_dir, 'data/bangs.json')) as json_file:
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
