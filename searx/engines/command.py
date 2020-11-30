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
'''


import re
from os.path import expanduser, isabs, realpath, commonprefix
from shlex import split as shlex_split
from subprocess import Popen, PIPE
from threading import Thread

from searx import logger


offline = True
paging = True
command = []
delimiter = {}
parse_regex = {}
query_type = ''
query_enum = []
environment_variables = {}
working_dir = realpath('.')
result_separator = '\n'
result_template = 'key-value.html'
timeout = 4.0

_command_logger = logger.getChild('command')
_compiled_parse_regex = {}


def init(engine_settings):
    check_parsing_options(engine_settings)

    if 'command' not in engine_settings:
        raise ValueError('engine command : missing configuration key: command')

    global command, working_dir, result_template, delimiter, parse_regex, timeout, environment_variables

    command = engine_settings['command']

    if 'working_dir' in engine_settings:
        working_dir = engine_settings['working_dir']
        if not isabs(engine_settings['working_dir']):
            working_dir = realpath(working_dir)

    if 'parse_regex' in engine_settings:
        parse_regex = engine_settings['parse_regex']
        for result_key, regex in parse_regex.items():
            _compiled_parse_regex[result_key] = re.compile(regex, flags=re.MULTILINE)
    if 'delimiter' in engine_settings:
        delimiter = engine_settings['delimiter']

    if 'environment_variables' in engine_settings:
        environment_variables = engine_settings['environment_variables']


def search(query, params):
    cmd = _get_command_to_run(query)
    if not cmd:
        return []

    results = []
    reader_thread = Thread(target=_get_results_from_process, args=(results, cmd, params['pageno']))
    reader_thread.start()
    reader_thread.join(timeout=timeout)

    return results


def _get_command_to_run(query):
    params = shlex_split(query.decode('utf-8'))
    __check_query_params(params)

    cmd = []
    for c in command:
        if c == '{{QUERY}}':
            cmd.extend(params)
        else:
            cmd.append(c)

    return cmd


def _get_results_from_process(results, cmd, pageno):
    leftover = ''
    count = 0
    start, end = __get_results_limits(pageno)
    with Popen(cmd, stdout=PIPE, stderr=PIPE, env=environment_variables) as process:
        line = process.stdout.readline()
        while line:
            buf = leftover + line.decode('utf-8')
            raw_results = buf.split(result_separator)
            if raw_results[-1]:
                leftover = raw_results[-1]
            raw_results = raw_results[:-1]

            for raw_result in raw_results:
                result = __parse_single_result(raw_result)
                if result is None:
                    _command_logger.debug('skipped result:', raw_result)
                    continue

                if start <= count and count <= end:
                    result['template'] = result_template
                    results.append(result)

                count += 1
                if end < count:
                    return results

            line = process.stdout.readline()

        return_code = process.wait(timeout=timeout)
        if return_code != 0:
            raise RuntimeError('non-zero return code when running command', cmd, return_code)


def __get_results_limits(pageno):
    start = (pageno - 1) * 10
    end = start + 9
    return start, end


def __check_query_params(params):
    if not query_type:
        return

    if query_type == 'path':
        query_path = params[-1]
        query_path = expanduser(query_path)
        if commonprefix([realpath(query_path), working_dir]) != working_dir:
            raise ValueError('requested path is outside of configured working directory')
    elif query_type == 'enum' and len(query_enum) > 0:
        for param in params:
            if param not in query_enum:
                raise ValueError('submitted query params is not allowed', param, 'allowed params:', query_enum)


def check_parsing_options(engine_settings):
    """ Checks if delimiter based parsing or regex parsing is configured correctly """

    if 'delimiter' not in engine_settings and 'parse_regex' not in engine_settings:
        raise ValueError('failed to init settings for parsing lines: missing delimiter or parse_regex')
    if 'delimiter' in engine_settings and 'parse_regex' in engine_settings:
        raise ValueError('failed to init settings for parsing lines: too many settings')

    if 'delimiter' in engine_settings:
        if 'chars' not in engine_settings['delimiter'] or 'keys' not in engine_settings['delimiter']:
            raise ValueError


def __parse_single_result(raw_result):
    """ Parses command line output based on configuration """

    result = {}

    if delimiter:
        elements = raw_result.split(delimiter['chars'], maxsplit=len(delimiter['keys']) - 1)
        if len(elements) != len(delimiter['keys']):
            return {}
        for i in range(len(elements)):
            result[delimiter['keys'][i]] = elements[i]

    if parse_regex:
        for result_key, regex in _compiled_parse_regex.items():
            found = regex.search(raw_result)
            if not found:
                return {}
            result[result_key] = raw_result[found.start():found.end()]

    return result
