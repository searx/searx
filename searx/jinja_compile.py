import jinja2
import tempfile

from searx import logger
logger = logger.getChild('jinja_compile')

def compile(app):
    env = app.jinja_env
    # archive = tempfile.TemporaryFile()
    _, archive = tempfile.mkstemp(suffix='.zip', prefix='searx')
    # archive.close = dummy
    env.compile_templates(archive, 
                          zip='stored',
                          py_compile=True,
                          log_function=logger.debug,
                          ignore_errors=False)
    app.jinja_env= env.overlay(loader=jinja2.loaders.ModuleLoader(archive))
