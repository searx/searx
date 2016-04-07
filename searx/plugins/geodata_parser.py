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

# match on valid sexagesimal and decimal coordinates
regex_coord = re.compile(ur"^(\+|-)?\s*0?([0-8]?[0-9]|90)(\.[0-9]+)?\s*"
                         ur"(\u00B0(\s*([0-5]?[0-9]|60)(\.[0-9]+)?\s*('|\u00B4)"
                         ur"(\s*([0-5]?[0-9]|60)(\.[0-9]+)?\s*(''|\"))?)?)?\s*(N|S)?\s*"
                         ur"(\+|-)?\s*(((1[0-7]|(0?[0-9])?)[0-9])|180)(\.[0-9]+)?\s*"
                         ur"(\u00B0(\s*([0-5]?[0-9]|60)(\.[0-9]+)?\s*('|\u00B4)"
                         ur"(\s*([0-5]?[0-9]|60)(\.[0-9]+)?\s*(''|\"))?)?)?\s*(W|E)?$",
                         re.UNICODE)

logger = logger.getChild('plugins.geodata_parser')


def coord_from_locator(locator):
    ''' calculate latitude and longitude using qth-locator '''
    # remove spaces from start and end of locator and convert to upper cases
    locator = locator.lstrip().rstrip().upper()

    lat = -90.
    lng = -180.
    factor = 18. / 24.

    # split locator in groups of 2 characters
    locator_groups = [locator[i:i + 2] for i in range(0, len(locator), 2)]

    # calculate lat and lng of locator
    for locator_part in locator_groups:
        if locator_part.isalpha():
            # TODO: test if only correct characters are used
            factor *= 24.
            lng += (ord(locator_part[0]) - ord('A')) * (360. / factor)
            lat += (ord(locator_part[1]) - ord('A')) * (180. / factor)
        elif locator_part.isdecimal():
            factor *= 10.
            lng += (ord(locator_part[0]) - ord('0')) * (360. / factor)
            lat += (ord(locator_part[1]) - ord('0')) * (180. / factor)
        else:
            # if locator is not valid, return None
            logger.debug("invalid locator-query: '{0}'".format(locator.encode("utf8")))
            lat = lng = None
            break

    return lat, lng


class GeodataParser(object):
    def __init__(self, query):
        self.lng = None
        self.lat = None

        self.raw_tokens = []
        self.token_iterator = iter([])
        self.token = None
        self.la = None

        self.scanner(query)

    def scanner(self, query):
        self.raw_tokens = re.split(ur"\s+|([NWSE])|(-)|(\+)|(\u00B0)|(''|')|(\")|(\u00B4)", query)
        self.raw_tokens = filter(None, self.raw_tokens)

    def init_parser(self):
        self.token_iterator = iter(self.raw_tokens)

        self.next_token()
        return self.next_token()

    def next_token(self):
        try:
            self.token = self.la
            self.la = self.token_iterator.next()
        except StopIteration:
            self.la = None

        return self.token

    def parse(self):
        self.lng = None
        self.lat = None
        self.init_parser()

        self.lat = self.parse_coordinate()
        if self.lat is None or self.lat > 90 or self.lat < -90:
            return None, None

        self.lng = self.parse_coordinate()
        if self.lng is None or self.lng > 180 or self.lng < -180:
            return None, None

        return self.lat, self.lng

    def parse_coordinate(self):
        '''
            EBNF-Grammar:
            ---------------------------------
            parse_coordinate
            =
            ["+"|"-"]
            float
            [ u'\u00B0'
                [ float [ "'" | u'\u00B4' ]
                    [ float ["''"|"\""] ]
                ]
            ]
            [ ["N"|"E"] | ["W"|"S"] ]
            ;
            ---------------------------------
        '''
        coord = None
        multiplicator = None

        if self.token == '+':
            multiplicator = 1
            self.next_token()
        elif self.token == '-':
            multiplicator = -1
            self.next_token()

        if self.token is not None and re.match("[0-9]+(.[0-9]+)?", self.token):
            coord = float(self.token)
            self.next_token()
        else:
            logger.debug("invalid token: '{0}'".format(str(self.token).encode("utf8")))
            return None

        if self.token == u'\u00B0':
            self.next_token()
            if self.token is not None and re.match("[0-9]+(.[0-9]+)?", self.token):
                if self.la == "'" or self.la == u'\u00B4':
                    coord += float(self.token) * 1. / 60.
                    self.next_token()
                    self.next_token()
                    if self.token is not None and re.match("[0-9]+(.[0-9]+)?", self.token):
                        if self.la == "''" or self.la == '"':
                            coord += float(self.token) * 1. / 60. / 60.
                            self.next_token()
                            self.next_token()

        if self.token in ['S', 'W']:
            multiplicator = -1
            self.next_token()
        elif self.token in ['N', 'E']:
            multiplicator = 1
            self.next_token()

        if not multiplicator:
            multiplicator = 1

        return coord * multiplicator


def get_locator(lat, lng, accuracy=3):
    return_string = ""
    lng += 180.
    lat += 90.
    factor = 18. / 24.

    for i in range(accuracy):
        if not i % 2:
            factor *= 24.
            if factor == 18.:
                return_string += chr(int(lng / (360. / factor)) + ord('A'))
                return_string += chr(int(lat / (180. / factor)) + ord('A'))
            else:
                return_string += chr(int(lng / (360. / factor)) + ord('a'))
                return_string += chr(int(lat / (180. / factor)) + ord('a'))
        else:
            factor *= 10.
            return_string += chr(int(lng / (360. / factor)) + ord('0'))
            return_string += chr(int(lat / (180. / factor)) + ord('0'))

        lng %= 360. / factor
        lat %= 180. / factor

    return return_string


def get_coord_decimal(lat, lng):
    return_string = ""
    cardinal_direction = None

    # get latitude
    if lat >= 0:
        cardinal_direction = 'N'
    else:
        cardinal_direction = 'S'
    return_string += u"{0:1.5f}\u00B0{1} ".format(abs(lat), cardinal_direction)

    # get longitude
    if lng >= 0:
        cardinal_direction = 'E'
    else:
        cardinal_direction = 'W'
    return_string += u"{0:1.5f}\u00B0{1}".format(abs(lng), cardinal_direction)

    return return_string


def get_coord_sexagesimal(lat, lng):
    return_string = ""
    cardinal_direction = None

    # get latitude
    if lat >= 0:
        cardinal_direction = 'N'
    else:
        cardinal_direction = 'S'
    return_string += u"{0}\u00B0{1}'{2:1.3g}\"{3} ".format(int(abs(lat)),
                                                           int(divmod(lat, 1)[1] * 60),
                                                           float(divmod((lat * 60), 1)[1] * 60),
                                                           cardinal_direction)

    # get longitude
    if lng >= 0:
        cardinal_direction = 'E'
    else:
        cardinal_direction = 'W'
    return_string += u"{0}\u00B0{1}'{2:1.3g}\"{3}".format(int(abs(lng)),
                                                          int(divmod(lng, 1)[1] * 60),
                                                          float(divmod((lng * 60), 1)[1] * 60),
                                                          cardinal_direction)

    return return_string


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

    if regex_coord.match(query):
        parser = GeodataParser(query)
        lat, lng = parser.parse()

    # TODO: improve output styling
    if lat is not None:
        ctx['search'].result_container.answers.add('locator: {0}'.format(get_locator(lat, lng)))
        ctx['search'].result_container.answers.add(u'decimal: {0}'.format(get_coord_decimal(lat, lng)))
        ctx['search'].result_container.answers.add(u'sexagesimal: {0}'.format(get_coord_sexagesimal(lat, lng)))

    return True
