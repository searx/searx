# See https://github.com/searx/searx/issues/2609
# Author: <a.mathew@outlook.com>

from searx import searx_dir
from searx.plugins import logger
from os.path import join as pathJoin
from flask_babel import gettext


name = gettext("Hits rewrite")
description = gettext("Rewrite hits to custom endpoints")
default_on = False
preference_section = "general"

configPath = pathJoin(searx_dir, "plugins/genericRewrites/config.yml")
config = None
parsed = "parsed_url"

logger = logger.getChild("generic_url_rewrite")


def get_config():
    """get config"""
    global config
    if not config:
        config = getConfigDict(configPath)
    if config:
        return config
    return False


def getConfigDict(configFile):
    try:
        ourDict = {}
        with open(configFile) as fobj:
            for entry in fobj:
                splat = entry.split(":")
                if len(splat) != 2:
                    continue
                wonky = [1 for i in splat if not i.strip()]
                if wonky:
                    continue
                key = splat[0].strip()
                val = splat[1].strip()
                ourDict[key] = val
        return ourDict
    except Exception as e:
        raise SearxSettingsException(e, file_name) from e


def rewriteUrl(result, newHostname):
    splat = result["url"].split("/")
    splat[2] = newHostname
    newUrl = "/".join(splat)
    result["url"] = newUrl

    parsedUrl = result[parsed]
    snu = "{url}:{port}".format(url=newUrl, port=parsedUrl.port)
    newParsed = parsedUrl._replace(netloc=snu)
    result[parsed] = newParsed


def on_result(request, search, result):
    if parsed not in result:
        return True
    config = get_config()
    if not config:
        return True
    newHostname = config.get(result[parsed].hostname)
    if newHostname:
        rewriteUrl(result, newHostname)

    return True
