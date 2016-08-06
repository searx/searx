"""
 Wikipedia (Web)

 @website     https://{language}.wikipedia.org
 @provide-api yes

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, infobox
"""

from json import loads
from urllib import urlencode, quote

supported_languages = ["en", "sv", "ceb", "de", "nl", "fr", "ru", "it", "es", "war",
                       "pl", "vi", "ja", "pt", "zh", "uk", "ca", "fa", "no", "sh",
                       "ar", "fi", "hu", "id", "ro", "cs", "ko", "sr", "ms", "tr",
                       "eu", "eo", "min", "bg", "da", "kk", "sk", "hy", "he", "zh-min-nan",
                       "lt", "hr", "sl", "et", "ce", "gl", "nn", "uz", "la", "vo",
                       "el", "simple", "be", "az", "th", "ur", "ka", "hi", "oc", "ta",
                       "mk", "mg", "new", "lv", "cy", "bs", "tt", "tl", "te", "pms",
                       "be-tarask", "br", "sq", "ky", "ht", "jv", "tg", "ast", "zh-yue", "lb",
                       "mr", "ml", "bn", "pnb", "is", "af", "sco", "ga", "ba", "fy",
                       "cv", "lmo", "sw", "my", "an", "yo", "ne", "io", "gu", "nds",
                       "scn", "bpy", "pa", "ku", "als", "kn", "bar", "ia", "qu", "su",
                       "ckb", "bat-smg", "mn", "arz", "nap", "wa", "bug", "gd", "yi", "map-bms",
                       "am", "mzn", "fo", "si", "nah", "li", "sah", "vec", "hsb", "or",
                       "os", "mrj", "sa", "hif", "mhr", "roa-tara", "azb", "pam", "ilo",
                       "sd", "ps", "se", "mi", "bh", "eml", "bcl", "xmf", "diq", "hak",
                       "gan", "glk", "vls", "nds-nl", "rue", "bo", "fiu-vro", "co", "sc",
                       "tk", "csb", "lrc", "vep", "wuu", "km", "szl", "gv", "crh", "kv",
                       "zh-classical", "frr", "zea", "as", "so", "kw", "nso", "ay", "stq",
                       "udm", "cdo", "nrm", "ie", "koi", "rm", "pcd", "myv", "mt", "fur",
                       "ace", "lad", "gn", "lij", "dsb", "dv", "cbk-zam", "ext", "gom",
                       "kab", "ksh", "ang", "mai", "mwl", "lez", "gag", "ln", "ug", "pi",
                       "pag", "frp", "sn", "nv", "av", "pfl", "haw", "xal", "krc", "kaa",
                       "rw", "bxr", "pdc", "to", "kl", "nov", "arc", "kbd", "lo", "bjn",
                       "pap", "ha", "tet", "ki", "tyv", "tpi", "na", "lbe", "ig", "jbo",
                       "roa-rup", "ty", "jam", "za", "kg", "mdf", "lg", "wo", "srn", "ab",
                       "ltg", "zu", "sm", "chr", "om", "tn", "chy", "rmy", "cu", "tw", "tum",
                       "xh", "bi", "rn", "pih", "got", "ss", "pnt", "bm", "ch", "mo", "ts",
                       "ady", "iu", "st", "ee", "ny", "fj", "ks", "ak", "ik", "sg", "ve",
                       "dz", "ff", "ti", "cr", "ng", "cho", "kj", "mh", "ho", "ii", "aa", "mus", "hz", "kr"]

# search-url
base_url = 'https://{language}.wikipedia.org/'
search_postfix = 'w/api.php?'\
    'action=query'\
    '&format=json'\
    '&{query}'\
    '&prop=extracts|pageimages'\
    '&exintro'\
    '&explaintext'\
    '&pithumbsize=300'\
    '&redirects'


# set language in base_url
def url_lang(lang):
    lang = lang.split('-')[0]
    if lang == 'all' or lang not in supported_languages:
        language = 'en'
    else:
        language = lang

    return base_url.format(language=language)


# do search-request
def request(query, params):
    if query.islower():
        query += '|' + query.title()

    params['url'] = url_lang(params['language']) \
        + search_postfix.format(query=urlencode({'titles': query}))

    return params


# get first meaningful paragraph
# this should filter out disambiguation pages and notes above first paragraph
# "magic numbers" were obtained by fine tuning
def extract_first_paragraph(content, title, image):
    first_paragraph = None

    failed_attempts = 0
    for paragraph in content.split('\n'):

        starts_with_title = paragraph.lower().find(title.lower(), 0, len(title) + 35)
        length = len(paragraph)

        if length >= 200 or (starts_with_title >= 0 and (image or length >= 150)):
            first_paragraph = paragraph
            break

        failed_attempts += 1
        if failed_attempts > 3:
            return None

    return first_paragraph


# get response from search-request
def response(resp):
    results = []

    search_result = loads(resp.content)

    # wikipedia article's unique id
    # first valid id is assumed to be the requested article
    for article_id in search_result['query']['pages']:
        page = search_result['query']['pages'][article_id]
        if int(article_id) > 0:
            break

    if int(article_id) < 0:
        return []

    title = page.get('title')

    image = page.get('thumbnail')
    if image:
        image = image.get('source')

    extract = page.get('extract')

    summary = extract_first_paragraph(extract, title, image)
    if not summary:
        return []

    # link to wikipedia article
    wikipedia_link = url_lang(resp.search_params['language']) \
        + 'wiki/' + quote(title.replace(' ', '_').encode('utf8'))

    results.append({'url': wikipedia_link, 'title': title})

    results.append({'infobox': title,
                    'id': wikipedia_link,
                    'content': summary,
                    'img_src': image,
                    'urls': [{'title': 'Wikipedia', 'url': wikipedia_link}]})

    return results
