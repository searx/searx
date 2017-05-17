from sys import version_info
from functools import reduce
from operator import mul

from flask_babel import gettext

if version_info[0] == 3:
    unicode = str

keywords = ('min',
            'max',
            'avg',
            'sum',
            'prod')


# required answerer function
# can return a list of results (any result type) for a given query
def answer(query):
    parts = query.query.split()

    if len(parts) < 2:
        return []

    try:
        args = list(map(float, parts[1:]))
    except:
        return []

    func = parts[0]
    answer = None

    if func == b'min':
        answer = min(args)
    elif func == b'max':
        answer = max(args)
    elif func == b'avg':
        answer = sum(args) / len(args)
    elif func == b'sum':
        answer = sum(args)
    elif func == b'prod':
        answer = reduce(mul, args, 1)

    if answer is None:
        return []

    return [{'answer': unicode(answer)}]


# required answerer function
# returns information about the answerer
def self_info():
    return {'name': gettext('Statistics functions'),
            'description': gettext('Compute {functions} of the arguments').format(functions='/'.join(keywords)),
            'examples': ['avg 123 548 2.04 24.2']}
