# SPDX-License-Identifier: AGPL-3.0-or-later

import sys
import os
import argparse

import searx.search
import searx.search.checker
from searx.search import processors
from searx.engines import engine_shortcuts


if sys.stdout.isatty() and os.environ.get('TERM') not in ['dumb', 'unknown']:
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
    BOLD_SEQ = "\033[1m"
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = map(lambda i: COLOR_SEQ % (30 + i), range(8))
else:
    RESET_SEQ = ""
    COLOR_SEQ = ""
    BOLD_SEQ = ""
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = "", "", "", "", "", "", "", ""


def iter_processor(engine_name_list):
    if len(engine_name_list) > 0:
        for name in engine_name_list:
            name = engine_shortcuts.get(name, name)
            processor = processors.get(name)
            if processor is not None:
                yield name, processor
            else:
                print(BOLD_SEQ, 'Engine ', '%-30s' % name, RESET_SEQ, RED, ' Not found ', RESET_SEQ)
    else:
        for name, processor in searx.search.processors.items():
            yield name, processor


def run(engine_name_list):
    searx.search.initialize()
    broken_urls = []
    for name, processor in iter_processor(engine_name_list):
        if sys.stdout.isatty():
            print(BOLD_SEQ, 'Engine ', '%-30s' % name, RESET_SEQ, WHITE, ' Checking', RESET_SEQ)
        checker = searx.search.checker.Checker(processor)
        checker.run()
        if checker.test_results.succesfull:
            print(BOLD_SEQ, 'Engine ', '%-30s' % name, RESET_SEQ, GREEN, ' OK', RESET_SEQ)
        else:
            errors = [test_name + ': ' + error for test_name, error in checker.test_results]
            print(BOLD_SEQ, 'Engine ', '%-30s' % name, RESET_SEQ, RED, ' Error ', str(errors), RESET_SEQ)

        broken_urls += checker.test_results.broken_urls

    for url in broken_urls:
        print('Error fetching', url)


def main():
    parser = argparse.ArgumentParser(description='Check searx engines.')
    parser.add_argument('engine_name_list', metavar='engine name', type=str, nargs='*',
                        help='engines name or shortcut list. Empty for all engines.')
    args = parser.parse_args()
    run(args.engine_name_list)


if __name__ == '__main__':
    main()
