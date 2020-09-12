'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2013- by Adam Tauber, <asciimoo@gmail.com>
'''

import re
from urllib.parse import urlparse
from lxml import etree
from os import listdir, environ
from os.path import isfile, isdir, join
from searx.plugins import logger
from flask_babel import gettext
from searx import searx_dir


name = "HTTPS rewrite"
description = gettext('Rewrite HTTP links to HTTPS if possible')
default_on = True
preference_section = 'privacy'

if 'SEARX_HTTPS_REWRITE_PATH' in environ:
    rules_path = environ['SEARX_rules_path']
else:
    rules_path = join(searx_dir, 'plugins/https_rules')

logger = logger.getChild("https_rewrite")

# https://gitweb.torproject.org/\
# pde/https-everywhere.git/tree/4.0:/src/chrome/content/rules

# HTTPS rewrite rules
https_rules = []


# load single ruleset from a xml file
def load_single_https_ruleset(rules_path):
    ruleset = ()

    # init parser
    parser = etree.XMLParser()

    # load and parse xml-file
    try:
        tree = etree.parse(rules_path, parser)
    except:
        # TODO, error message
        return ()

    # get root node
    root = tree.getroot()

    # check if root is a node with the name ruleset
    # TODO improve parsing
    if root.tag != 'ruleset':
        return ()

    # check if rule is deactivated by default
    if root.attrib.get('default_off'):
        return ()

    # check if rule does only work for specific platforms
    if root.attrib.get('platform'):
        return ()

    hosts = []
    rules = []
    exclusions = []

    # parse childs from ruleset
    for ruleset in root:
        # this child define a target
        if ruleset.tag == 'target':
            # check if required tags available
            if not ruleset.attrib.get('host'):
                continue

            # convert host-rule to valid regex
            host = ruleset.attrib.get('host')\
                .replace('.', r'\.').replace('*', '.*')

            # append to host list
            hosts.append(host)

        # this child define a rule
        elif ruleset.tag == 'rule':
            # check if required tags available
            if not ruleset.attrib.get('from')\
               or not ruleset.attrib.get('to'):
                continue

            # TODO hack, which convert a javascript regex group
            # into a valid python regex group
            rule_from = ruleset.attrib['from'].replace('$', '\\')
            if rule_from.endswith('\\'):
                rule_from = rule_from[:-1] + '$'
            rule_to = ruleset.attrib['to'].replace('$', '\\')
            if rule_to.endswith('\\'):
                rule_to = rule_to[:-1] + '$'

            # TODO, not working yet because of the hack above,
            # currently doing that in webapp.py
            # rule_from_rgx = re.compile(rule_from, re.I)

            # append rule
            try:
                rules.append((re.compile(rule_from, re.I | re.U), rule_to))
            except:
                # TODO log regex error
                continue

        # this child define an exclusion
        elif ruleset.tag == 'exclusion':
            # check if required tags available
            if not ruleset.attrib.get('pattern'):
                continue

            exclusion_rgx = re.compile(ruleset.attrib.get('pattern'))

            # append exclusion
            exclusions.append(exclusion_rgx)

    # convert list of possible hosts to a simple regex
    # TODO compress regex to improve performance
    try:
        target_hosts = re.compile('^(' + '|'.join(hosts) + ')', re.I | re.U)
    except:
        return ()

    # return ruleset
    return (target_hosts, rules, exclusions)


# load all https rewrite rules
def load_https_rules(rules_path):
    # check if directory exists
    if not isdir(rules_path):
        logger.error("directory not found: '" + rules_path + "'")
        return

    # search all xml files which are stored in the https rule directory
    xml_files = [join(rules_path, f)
                 for f in listdir(rules_path)
                 if isfile(join(rules_path, f)) and f[-4:] == '.xml']

    # load xml-files
    for ruleset_file in xml_files:
        # calculate rewrite-rules
        ruleset = load_single_https_ruleset(ruleset_file)

        # skip if no ruleset returned
        if not ruleset:
            continue

        # append ruleset
        https_rules.append(ruleset)

    logger.info('{n} rules loaded'.format(n=len(https_rules)))


def https_url_rewrite(result):
    skip_https_rewrite = False
    # check if HTTPS rewrite is possible
    for target, rules, exclusions in https_rules:

        # check if target regex match with url
        if target.match(result['parsed_url'].netloc):
            # process exclusions
            for exclusion in exclusions:
                # check if exclusion match with url
                if exclusion.match(result['url']):
                    skip_https_rewrite = True
                    break

            # skip https rewrite if required
            if skip_https_rewrite:
                break

            # process rules
            for rule in rules:
                try:
                    new_result_url = rule[0].sub(rule[1], result['url'])
                except:
                    break

                # parse new url
                new_parsed_url = urlparse(new_result_url)

                # continiue if nothing was rewritten
                if result['url'] == new_result_url:
                    continue

                # get domainname from result
                # TODO, does only work correct with TLD's like
                #  asdf.com, not for asdf.com.de
                # TODO, using publicsuffix instead of this rewrite rule
                old_result_domainname = '.'.join(
                    result['parsed_url'].hostname.split('.')[-2:])
                new_result_domainname = '.'.join(
                    new_parsed_url.hostname.split('.')[-2:])

                # check if rewritten hostname is the same,
                # to protect against wrong or malicious rewrite rules
                if old_result_domainname == new_result_domainname:
                    # set new url
                    result['url'] = new_result_url

            # target has matched, do not search over the other rules
            break
    return result


def on_result(request, search, result):
    if 'parsed_url' not in result:
        return True

    if result['parsed_url'].scheme == 'http':
        https_url_rewrite(result)
    return True


load_https_rules(rules_path)
