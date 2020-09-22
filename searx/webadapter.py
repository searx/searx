from searx.exceptions import SearxParameterException
from searx.query import RawTextQuery, VALID_LANGUAGE_CODE
from searx.engines import categories, engines
from searx.search import SearchQuery, EngineRef


# remove duplicate queries.
# FIXME: does not fix "!music !soundcloud", because the categories are 'none' and 'music'
def deduplicate_engineref_list(engineref_list):
    engineref_dict = {q.category + '|' + q.name: q for q in engineref_list}
    return engineref_dict.values()


def validate_engineref_list(engineref_list, preferences):
    """
    Validate query_engines according to the preferences
        Returns:
            list of existing engines with a validated token
            list of unknown engine
            list of engine with invalid token according to the preferences
    """
    valid = []
    unknown = []
    no_token = []
    for engineref in engineref_list:
        if engineref.name not in engines:
            unknown.append(engineref)
            continue

        engine = engines[engineref.name]
        if not preferences.validate_token(engine):
            no_token.append(engineref)
            continue

        valid.append(engineref)
    return valid, unknown, no_token


def parse_pageno(form):
    pageno_param = form.get('pageno', '1')
    if not pageno_param.isdigit() or int(pageno_param) < 1:
        raise SearxParameterException('pageno', pageno_param)
    return int(pageno_param)


def parse_lang(raw_text_query, form, preferences):
    # get language
    # set specific language if set on request, query or preferences
    # TODO support search with multible languages
    if len(raw_text_query.languages):
        query_lang = raw_text_query.languages[-1]
    elif 'language' in form:
        query_lang = form.get('language')
    else:
        query_lang = preferences.get_value('language')

    # check language
    if not VALID_LANGUAGE_CODE.match(query_lang):
        raise SearxParameterException('language', query_lang)

    return query_lang


def parse_safesearch(form, preferences):
    if 'safesearch' in form:
        query_safesearch = form.get('safesearch')
        # first check safesearch
        if not query_safesearch.isdigit():
            raise SearxParameterException('safesearch', query_safesearch)
        query_safesearch = int(query_safesearch)
    else:
        query_safesearch = preferences.get_value('safesearch')

    # safesearch : second check
    if query_safesearch < 0 or query_safesearch > 2:
        raise SearxParameterException('safesearch', query_safesearch)

    return query_safesearch


def parse_time_range(form):
    query_time_range = form.get('time_range')
    # check time_range
    query_time_range = None if query_time_range in ('', 'None') else query_time_range
    if query_time_range not in (None, 'day', 'week', 'month', 'year'):
        raise SearxParameterException('time_range', query_time_range)
    return query_time_range


def parse_timeout(raw_text_query, form):
    query_timeout = raw_text_query.timeout_limit
    if query_timeout is None and 'timeout_limit' in form:
        raw_time_limit = form.get('timeout_limit')
        if raw_time_limit in ['None', '']:
            return None
        else:
            try:
                return float(raw_time_limit)
            except ValueError:
                raise SearxParameterException('timeout_limit', raw_time_limit)


def get_search_query_from_webapp(preferences, form):
    # no text for the query ?
    if not form.get('q'):
        raise SearxParameterException('q', '')

    # set blocked engines
    disabled_engines = preferences.engines.get_disabled()

    # parse query, if tags are set, which change
    # the serch engine or search-language
    raw_text_query = RawTextQuery(form['q'], disabled_engines)

    # set query
    query = raw_text_query.getQuery()
    query_pageno = parse_pageno(form)
    query_lang = parse_lang(raw_text_query, form, preferences)
    query_safesearch = parse_safesearch(form, preferences)
    query_time_range = parse_time_range(form)
    query_timeout = parse_timeout(raw_text_query, form)
    external_bang = raw_text_query.external_bang

    # query_categories
    query_engineref_list = raw_text_query.enginerefs
    query_categories = []

    # if engines are calculated from query,
    # set categories by using that informations
    if query_engineref_list and raw_text_query.specific:
        additional_categories = set()
        for engineref in query_engineref_list:
            if engineref.from_bang:
                additional_categories.add('none')
            else:
                additional_categories.add(engineref.category)
        query_categories = list(additional_categories)

    # otherwise, using defined categories to
    # calculate which engines should be used
    else:
        # set categories/engines
        load_default_categories = True
        for pd_name, pd in form.items():
            if pd_name == 'categories':
                query_categories.extend(categ for categ in map(str.strip, pd.split(',')) if categ in categories)
            elif pd_name == 'engines':
                pd_engines = [EngineRef(engineref, engines[engineref].categories[0])
                              for engine in map(str.strip, pd.split(',')) if engine in engines]
                if pd_engines:
                    query_engineref_list.extend(pd_engines)
                    load_default_categories = False
            elif pd_name.startswith('category_'):
                category = pd_name[9:]

                # if category is not found in list, skip
                if category not in categories:
                    continue

                if pd != 'off':
                    # add category to list
                    query_categories.append(category)
                elif category in query_categories:
                    # remove category from list if property is set to 'off'
                    query_categories.remove(category)

        if not load_default_categories:
            if not query_categories:
                query_categories = list(set(engine['category']
                                            for engine in query_engineref_list))
        else:
            # if no category is specified for this search,
            # using user-defined default-configuration which
            # (is stored in cookie)
            if not query_categories:
                cookie_categories = preferences.get_value('categories')
                for ccateg in cookie_categories:
                    if ccateg in categories:
                        query_categories.append(ccateg)

            # if still no category is specified, using general
            # as default-category
            if not query_categories:
                query_categories = ['general']

            # using all engines for that search, which are
            # declared under the specific categories
            for categ in query_categories:
                query_engineref_list.extend(EngineRef(engine.name, categ)
                                            for engine in categories[categ]
                                            if (engine.name, categ) not in disabled_engines)

    query_engineref_list = deduplicate_engineref_list(query_engineref_list)
    query_engineref_list, query_engineref_list_unknown, query_engineref_list_notoken =\
        validate_engineref_list(query_engineref_list, preferences)
    external_bang = raw_text_query.external_bang

    return (SearchQuery(query, query_engineref_list, query_categories,
                        query_lang, query_safesearch, query_pageno,
                        query_time_range, query_timeout,
                        external_bang=external_bang),
            raw_text_query,
            query_engineref_list_unknown,
            query_engineref_list_notoken)
