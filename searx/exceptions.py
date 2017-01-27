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

(C) 2017- by Alexandre Flament, <alex@al-f.net>
'''


class SearxException(Exception):
    pass


class SearxParameterException(SearxException):

    def __init__(self, name, value):
        if value == '' or value is None:
            message = 'Empty ' + name + ' parameter'
        else:
            message = 'Invalid value "' + value + '" for parameter ' + name
        super(SearxParameterException, self).__init__(message)
        self.parameter_name = name
        self.parameter_value = value
