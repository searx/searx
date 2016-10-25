import jinja2
import tempfile
import weakref
from searx import logger

logger = logger.getChild('jinja_compile')
archives = weakref.WeakKeyDictionary()


def compile(app):
    archive = tempfile.NamedTemporaryFile(prefix='searx', suffix='.zip')
    env = app.jinja_env
    env.compile_templates(archive,
                          zip='stored',
                          py_compile=True,
                          log_function=logger.debug,
                          ignore_errors=False)
    app.jinja_env = env.overlay(loader=jinja2.loaders.ModuleLoader(archive.name))
    archives[app] = archive
