import sys

import searx.search
import searx.search.processors
import searx.search.checker


if sys.stdout.isatty():
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
    BOLD_SEQ = "\033[1m"
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = map(lambda i: COLOR_SEQ % (30 + i), range(8))
else:
    RESET_SEQ = ""
    COLOR_SEQ = ""
    BOLD_SEQ = ""
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = "", "", "", "", "", "", "", ""


def iter_processor():
    if len(sys.argv) > 1:
        for name, processor in searx.search.processors.items():
            if name in sys.argv:
                yield name, processor
    else:
        for name, processor in searx.search.processors.items():
            yield name, processor


def main():
    searx.search.initialize()
    broken_urls = []
    for name, processor in iter_processor():
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


if __name__ == '__main__':
    main()
