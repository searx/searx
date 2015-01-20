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

(C) 2015- by Thomas Pointhuber
'''

from sets import Set
import operator
import re


# Source:
# https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def levenshtein(s, t):
    ''' From Wikipedia article; Iterative with two matrix rows. '''
    # for this conditions, the result is easily computable
    if s == t:
        return 0
    elif len(s) == 0:
        return len(t)
    elif len(t) == 0:
        return len(s)

    v0 = [None] * (len(t) + 1)
    v1 = [None] * (len(t) + 1)

    for i in range(len(v0)):
        v0[i] = i
    for i in range(len(s)):
        v1[0] = i + 1
        for j in range(len(t)):
            cost = 0 if s[i] == t[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        for j in range(len(v0)):
            v0[j] = v1[j]

    return v1[len(t)]


def spell_corrections(query, dictionary, max_distance=3):
    ''' get all possible spell corrections from query using a provided dictionary '''
    corrections = {}

    for word in Set(dictionary):
        # if the lenght of dictionary and query differ to much, skip
        if abs(len(query)-len(word)) > max_distance:
            continue

        # calculate distance between query and word
        distance = levenshtein(query, word)

        # if distance is small enough, add to dictionary
        if distance <= max_distance:
            corrections[word] = distance

    # return spell corrections
    return corrections


def corrections_from_suggestions(query, suggestions):
    ''' get good spell corrections using suggestions '''
    dictionary = Set()

    # create dictionary from single suggestion words
    for suggestion in suggestions:
        words = suggestion.split()
        dictionary.update(words)

    spell_suggestions = []

    # split query, including whitespaces
    raw_query_parts = re.split(r'(\s+)', query)

    # TODO: currently, generating only one spell suggestions
    new_query = ''
    for query_part in raw_query_parts:
        # if query part contain less than 3 letters or only spaces, skip spell correction
        if len(query_part) < 3 or query_part.isspace():
            new_query = new_query + query_part
            continue

        # allowing bigger distance if query_part is long enought
        if len(query_part) < 10:
            max_distance = 2
        else:
            max_distance = 3

        # calculate spell corrections for this query part
        corrections = spell_corrections(query_part, dictionary, max_distance)

        # if no corrections is provided, use typed query_part
        if not len(corrections):
            new_query = new_query + query_part
            continue

        # sort corrections by distance
        sorted_corrections = sorted(corrections.items(), key=operator.itemgetter(1))

        # add best corrections to new query
        new_query = new_query + sorted_corrections[0][0]

    # if the new_query differ from the query, add to spell_suggestions
    if new_query.lower() != query.lower():
        spell_suggestions.append(new_query)

    # return spell suggestions
    return spell_suggestions
