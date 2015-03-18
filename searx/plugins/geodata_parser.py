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

(C) 2015 by Thomas Pointhuber
'''

from searx import logger
from flask.ext.babel import gettext
import re

name = "Geodata parser"
description = gettext('Parse geodata string and display it in different formats including map-view')
default_on = False  # TODO: finish plugin

# match on valid locators from AR09AX to AR09AX09AX09AX09AR09AR09
regex_locator = re.compile(r"^[A-R]{2}([0-9]{2}[A-X]{2}){1,5}([0-9]{2})?$")

# match on valid coordinates like "+19.228 -155.3" or "15.13N 12.889W"
regex_decimal_coord = re.compile(r"(|\+|-)\s*([0-8]?[0-9]|90)\.[0-9]+\s*(N|S|)\s*(|\+|-)\s*"
                                 "(((1[0-7]|(0?[0-9])?)[0-9])|180)\.[0-9]+\s*(W|E|)$")

logger = logger.getChild('plugins.geodata_parser')


def coord_from_locator(locator):
    ''' calculate latitude and longitude using qth-locator '''
    # remove spaces from start and end of locator and convert to upper cases
    locator = locator.lstrip().rstrip().upper()

    lat = -90.
    lng = -180.
    factor = 18./24.

    # split locator in groups of 2 characters
    locator_groups = [locator[i:i+2] for i in range(0, len(locator), 2)]

    # calculate lat and lng of locator
    for locator_part in locator_groups:
        if locator_part.isalpha():
            # TODO: test if only correct characters are used
            factor *= 24.
            lng += (ord(locator_part[0])-ord('A'))*(360./factor)
            lat += (ord(locator_part[1])-ord('A'))*(180./factor)
        elif locator_part.isdecimal():
            factor *= 10.
            lng += (ord(locator_part[0])-ord('0'))*(360./factor)
            lat += (ord(locator_part[1])-ord('0'))*(180./factor)
        else:
            # if locator is not valid, return None
            lat = lng = None
            break

    return lat, lng


def coord_from_decimal_coordinates(query):
    ''' calculate latitude and longitude using decimal coordinates '''
    lng = lat = None

    # help variables
    multiplicator = 1
    parse_lat = True
    skip_token = False

    # create tokens to parse query
    tokens = re.split(r'\s+|([NWSE])|(-)|(\+)', query)
    tokens = filter(None, tokens)

    # the last la-token is None
    tokens.append(None)

    # parse tokens with an simple LL(1) parser
    for token, la in zip(tokens, tokens[1:]):
        if parse_lat:
            # parse latitude
            if skip_token:
                skip_token = False
                parse_lat = False
                continue
            elif token == '+':
                multiplicator = 1
            elif token == '-':
                multiplicator = -1

            elif re.match("[0-9]+.[0-9]+", token):
                # check if la-token has something important
                if la == 'N':
                    multiplicator = 1
                    skip_token = True
                elif la == 'S':
                    multiplicator = -1
                    skip_token = True
                else:
                    parse_lat = False

                # calculate latitude
                lat = float(token) * multiplicator

                # check if number is out of range
                if lat > 90 or lat < -90:
                    lng = lat = None
                    break

                # reset multiplicator
                multiplicator = 1
            else:
                logger.error("unknow token: '{0}'".format(token))
        else:
            # parse longitude
            if skip_token:
                skip_token = False
                continue
            elif token == '+':
                multiplicator = 1
            elif token == '-':
                multiplicator = -1
            elif re.match("[0-9]+.[0-9]+", token):
                # check if la-token has something important
                if la == 'E':
                    multiplicator = 1
                    skip_token = True
                elif la == 'W':
                    multiplicator = -1
                    skip_token = True

                # calculate longitude
                lng = float(token) * multiplicator

                # check if number is out of range
                if lng > 180 or lng < -180:
                    lng = lat = None
                    break
            else:
                logger.error("unknow token: '{0}'".format(token))

    return lat, lng


# attach callback to the pre search hook
#  request: flask request object
#  ctx: the whole local context of the pre search hook
def pre_search(request, ctx):
    # remove spaces from start and end of string and convert to upper cases
    query = ctx['search'].query.lstrip().rstrip().upper()

    lat = lng = None

    if regex_locator.match(query):
        # if the query is a valid locator, calculate coordinates
        lat, lng = coord_from_locator(query)

    elif 'LOCATOR' in query:
        # if the word 'LOCATOR' is inside the query, search for valid locators
        for query_part in query.split():
            if regex_locator.match(query_part):
                # if more than one valid locator is possible, skip
                if lat is not None:
                    lat = lng = None
                    break
                lat, lng = coord_from_locator(query_part)

    elif regex_decimal_coord.match(query):
        # if the query is a valid decimal coordinate, calculate coordinates
        lat, lng = coord_from_decimal_coordinates(query)

    # TODO: improve output styling
    if lat is not None:
        ctx['search'].answers.add('lat: {0} lng: {1}'.format(lat, lng))

    return True
