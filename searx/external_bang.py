# SPDX-License-Identifier: AGPL-3.0-or-later

from urllib.parse import urljoin

from searx.data import EXTERNAL_BANGS


def get_node(external_bangs_db, bang):
    node = external_bangs_db['trie']
    after = ''
    before = ''
    for bang_letter in bang:
        after += bang_letter
        if after in node and isinstance(node, dict):
            node = node[after]
            before += after
            after = ''
    return node, before, after


def get_bang_definition_and_ac(external_bangs_db, bang):
    node, before, after = get_node(external_bangs_db, bang)

    bang_definition = None
    bang_ac_list = []
    if after != '':
        for k in node:
            if k.startswith(after):
                bang_ac_list.append(before + k)
    elif isinstance(node, dict):
        bang_definition = node.get('*')
        bang_ac_list = [before + k for k in node.keys() if k != '*']
    elif isinstance(node, str):
        bang_definition = node
        bang_ac_list = []

    return bang_definition, bang_ac_list


def resolve_bang_definition(bang_definition, query):
    url, rank = bang_definition.split(chr(1))
    url = url.replace(chr(2), query)
    if url.startswith('//'):
        url = 'https:' + url
    if not query:  # go to main instead of search page
        url = urljoin(url, '/')
    rank = int(rank) if len(rank) > 0 else 0
    return (url, rank)


def get_bang_definition_and_autocomplete(bang, external_bangs_db=None):
    global EXTERNAL_BANGS
    if external_bangs_db is None:
        external_bangs_db = EXTERNAL_BANGS

    bang_definition, bang_ac_list = get_bang_definition_and_ac(external_bangs_db, bang)

    new_autocomplete = []
    current = [*bang_ac_list]
    done = set()
    while len(current) > 0:
        bang_ac = current.pop(0)
        done.add(bang_ac)

        current_bang_definition, current_bang_ac_list = get_bang_definition_and_ac(external_bangs_db, bang_ac)
        if current_bang_definition:
            _, order = resolve_bang_definition(current_bang_definition, '')
            new_autocomplete.append((bang_ac, order))
        for new_bang in current_bang_ac_list:
            if new_bang not in done and new_bang not in current:
                current.append(new_bang)

    new_autocomplete.sort(key=lambda t: (-t[1], t[0]))
    new_autocomplete = list(map(lambda t: t[0], new_autocomplete))

    return bang_definition, new_autocomplete


def get_bang_url(search_query, external_bangs_db=None):
    """
    Redirects if the user supplied a correct bang search.
    :param search_query: This is a search_query object which contains preferences and the submitted queries.
    :return: None if the bang was invalid, else a string of the redirect url.
    """
    global EXTERNAL_BANGS
    if external_bangs_db is None:
        external_bangs_db = EXTERNAL_BANGS

    if search_query.external_bang:
        bang_definition, _ = get_bang_definition_and_ac(external_bangs_db, search_query.external_bang)
        return resolve_bang_definition(bang_definition, search_query.query)[0] if bang_definition else None

    return None
