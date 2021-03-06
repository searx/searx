
# See https://github.com/searx/searx/issues/2609
# Author: <a.mathew@outlook.com> 

from searx import searx_dir
from searx.plugins import logger
from os.path import join as pathJoin
from flask_babel import gettext
import urllib.parse


name = gettext("Hits rewrite")
description = gettext("Rewrite hits to custom endpoints")
default_on = False
preference_section = "general"

configPath = pathJoin(searx_dir, "plugins/genericRewrites/config.yml")
config = None
parsed = "parsed_url"

logger = logger.getChild("generic_url_rewrite")

# return config dict if we can
def getConfigDict(configPath) -> {}:
    try:
        ourDict = {}
        with open(configPath) as fobj:
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
    except:
        return {}
            

def get_config():
    global config
    if not config:
        config = getConfigDict(configPath)
    if config:
        return config 
    return False 

def rewriteUrl(result, newHostname):
    splat = result["url"].split("/")
    splat[2] = newHostname
    newUrl = "/".join(splat)
    result["url"] = newUrl

    parsedUrl = result[parsed]
    newParsed = parsedUrl._replace(netloc = "{newDest}:{port}".format(newDest=newUrl, port=parsedUrl.port))
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

