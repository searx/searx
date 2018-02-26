from os import listdir
from os.path import realpath, dirname, join, isdir
from sys import version_info
from searx.utils import load_module
from collections import defaultdict

if version_info[0] == 3:
    unicode = str


def file_loader():
    answerers_dir = dirname(realpath(__file__))
    answerers = []
    for filename in listdir(answerers_dir):
        if not isdir(join(answerers_dir, filename)) or filename.startswith('_'):
            continue
        module = load_module('answerer.py', join(answerers_dir, filename))
        if not hasattr(module, 'keywords') or not isinstance(module.keywords, tuple) or not len(module.keywords):
            exit(2)
        answerers.append(module)
    return answerers


class Answerers():
    def __init__(self, loader):
        self.loader = loader

    def get(self):
        return self.loader()

    def get_by_keywords(self):
        answerers = self.loader()
        by_keyword = defaultdict(list)
        for answerer in answerers:
            for keyword in answerer.keywords:
                for keyword in answerer.keywords:
                    by_keyword[keyword].append(answerer.answer)
        return by_keyword

    def ask(self, query):
        answerers_by_keywords = self.get_by_keywords()
        results = []
        query_parts = list(filter(None, query.query.split()))

        if query_parts[0] not in answerers_by_keywords:
            return results

        for answerer in answerers_by_keywords[query_parts[0]]:
            result = answerer(query)
            if result:
                results.append(result)
        return results
