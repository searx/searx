from searx.data import bangs_loader

# bangs data coming from the following url convert to json with
# https://raw.githubusercontent.com/jivesearch/jivesearch/master/bangs/bangs.toml
# https://pseitz.github.io/toml-to-json-online-converter/
# NOTE only use the get_bang_url

bangs_data = {}
for bang in bangs_loader()['bang']:
    for trigger in bang["triggers"]:
        bangs_data[trigger] = {x: y for x, y in bang.items() if x != "triggers"}


def get_bang_url(search_query):
    """
    Redirects if the user supplied a correct bang search.
    :param search_query: This is a search_query object which contains preferences and the submitted queries.
    :return: None if the bang was invalid, else a string of the redirect url.
    """

    if search_query.external_bang:
        query = search_query.query
        bang = _get_bang(search_query.external_bang)

        if bang and query:
            # TODO add region support.
            bang_url = bang["regions"]["default"]

            return bang_url.replace("{{{term}}}", query)
    return None


def _get_bang(user_bang):
    """
    Searches if the supplied user bang is available. Returns None if not found.
    :param user_bang: The parsed user bang. For example yt
    :return: Returns a dict with bangs data (check bangs_data.json for the structure)
    """
    return bangs_data.get(user_bang)
