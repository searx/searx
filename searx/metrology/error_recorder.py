import typing
import inspect
import logging
from json import JSONDecodeError
from urllib.parse import urlparse
from requests.exceptions import RequestException
from searx.exceptions import (SearxXPathSyntaxException, SearxEngineXPathException, SearxEngineAPIException,
                              SearxEngineAccessDeniedException)
from searx import logger


logging.basicConfig(level=logging.INFO)

errors_per_engines = {}


class ErrorContext:

    __slots__ = 'filename', 'function', 'line_no', 'code', 'exception_classname', 'log_message', 'log_parameters'

    def __init__(self, filename, function, line_no, code, exception_classname, log_message, log_parameters):
        self.filename = filename
        self.function = function
        self.line_no = line_no
        self.code = code
        self.exception_classname = exception_classname
        self.log_message = log_message
        self.log_parameters = log_parameters

    def __eq__(self, o) -> bool:
        if not isinstance(o, ErrorContext):
            return False
        return self.filename == o.filename and self.function == o.function and self.line_no == o.line_no\
            and self.code == o.code and self.exception_classname == o.exception_classname\
            and self.log_message == o.log_message and self.log_parameters == o.log_parameters

    def __hash__(self):
        return hash((self.filename, self.function, self.line_no, self.code, self.exception_classname, self.log_message,
                     self.log_parameters))

    def __repr__(self):
        return "ErrorContext({!r}, {!r}, {!r}, {!r}, {!r}, {!r})".\
            format(self.filename, self.line_no, self.code, self.exception_classname, self.log_message,
                   self.log_parameters)


def add_error_context(engine_name: str, error_context: ErrorContext) -> None:
    errors_for_engine = errors_per_engines.setdefault(engine_name, {})
    errors_for_engine[error_context] = errors_for_engine.get(error_context, 0) + 1
    logger.debug('⚠️ %s: %s', engine_name, str(error_context))


def get_trace(traces):
    previous_trace = traces[-1]
    for trace in reversed(traces):
        if trace.filename.endswith('searx/search.py'):
            if previous_trace.filename.endswith('searx/poolrequests.py'):
                return trace
            if previous_trace.filename.endswith('requests/models.py'):
                return trace
            return previous_trace
        previous_trace = trace
    return traces[-1]


def get_hostname(exc: RequestException) -> typing.Optional[None]:
    url = exc.request.url
    if url is None and exc.response is not None:
        url = exc.response.url
    return urlparse(url).netloc


def get_request_exception_messages(exc: RequestException)\
        -> typing.Tuple[typing.Optional[str], typing.Optional[str], typing.Optional[str]]:
    url = None
    status_code = None
    reason = None
    hostname = None
    if exc.request is not None:
        url = exc.request.url
    if url is None and exc.response is not None:
        url = exc.response.url
    if url is not None:
        hostname = str(urlparse(url).netloc)
    if exc.response is not None:
        status_code = str(exc.response.status_code)
        reason = exc.response.reason
    return (status_code, reason, hostname)


def get_messages(exc, filename) -> typing.Tuple:
    if isinstance(exc, JSONDecodeError):
        return (exc.msg, )
    if isinstance(exc, TypeError):
        return (str(exc), )
    if isinstance(exc, ValueError) and 'lxml' in filename:
        return (str(exc), )
    if isinstance(exc, RequestException):
        return get_request_exception_messages(exc)
    if isinstance(exc, SearxXPathSyntaxException):
        return (exc.xpath_str, exc.message)
    if isinstance(exc, SearxEngineXPathException):
        return (exc.xpath_str, exc.message)
    if isinstance(exc, SearxEngineAPIException):
        return (str(exc.args[0]), )
    if isinstance(exc, SearxEngineAccessDeniedException):
        return (exc.message, )
    return ()


def get_exception_classname(exc: Exception) -> str:
    exc_class = exc.__class__
    exc_name = exc_class.__qualname__
    exc_module = exc_class.__module__
    if exc_module is None or exc_module == str.__class__.__module__:
        return exc_name
    return exc_module + '.' + exc_name


def get_error_context(framerecords, exception_classname, log_message, log_parameters) -> ErrorContext:
    searx_frame = get_trace(framerecords)
    filename = searx_frame.filename
    function = searx_frame.function
    line_no = searx_frame.lineno
    code = searx_frame.code_context[0].strip()
    del framerecords
    return ErrorContext(filename, function, line_no, code, exception_classname, log_message, log_parameters)


def record_exception(engine_name: str, exc: Exception) -> None:
    framerecords = inspect.trace()
    try:
        exception_classname = get_exception_classname(exc)
        log_parameters = get_messages(exc, framerecords[-1][1])
        error_context = get_error_context(framerecords, exception_classname, None, log_parameters)
        add_error_context(engine_name, error_context)
    finally:
        del framerecords


def record_error(engine_name: str, log_message: str, log_parameters: typing.Optional[typing.Tuple] = None) -> None:
    framerecords = list(reversed(inspect.stack()[1:]))
    try:
        error_context = get_error_context(framerecords, None, log_message, log_parameters or ())
        add_error_context(engine_name, error_context)
    finally:
        del framerecords
