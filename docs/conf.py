# -*- coding: utf-8 -*-

import  sys, os
from searx.version import VERSION_STRING
from pallets_sphinx_themes import ProjectLink

GIT_URL = os.environ.get("GIT_URL", "https://github.com/asciimoo/searx")
GIT_BRANCH =os.environ.get("GIT_BRANCH", "master")
SEARX_URL = os.environ.get("SEARX_URL", "https://searx.me")
DOCS_URL = os.environ.get("DOCS_URL", "https://asciimoo.github.io/searx/")

# Project --------------------------------------------------------------

project = u'searx'
copyright = u'2015-2020, Adam Tauber, Noémi Ványi'
author = u'Adam Tauber'
release, version = VERSION_STRING, VERSION_STRING
highlight_language = 'none'

# General --------------------------------------------------------------

master_doc = "index"
source_suffix = '.rst'
numfig = True

exclude_patterns = ['build-templates/*.rst']

from searx import webapp
jinja_contexts = {
    'webapp': dict(**webapp.__dict__)
}

# usage::   lorem :patch:`f373169` ipsum
extlinks = {}

# upstream links
extlinks['wiki'] = ('https://github.com/asciimoo/searx/wiki/%s', ' ')
extlinks['pull'] = ('https://github.com/asciimoo/searx/pull/%s', 'PR ')

# links to custom brand
extlinks['origin'] = (GIT_URL + '/blob/' + GIT_BRANCH + '/%s', 'git://')
extlinks['patch'] = (GIT_URL + '/commit/%s', '#')
extlinks['search'] = (SEARX_URL + '/%s', '#')
extlinks['docs'] = (DOCS_URL + '/%s', 'docs: ')
extlinks['pypi'] = ('https://pypi.org/project/%s', 'PyPi: ')
extlinks['man'] = ('https://manpages.debian.org/jump?q=%s', '')
#extlinks['role'] = (
#    'https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-%s', '')
extlinks['duref'] = (
    'http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#%s', '')
extlinks['durole'] = (
    'http://docutils.sourceforge.net/docs/ref/rst/roles.html#%s', '')
extlinks['dudir'] =  (
    'http://docutils.sourceforge.net/docs/ref/rst/directives.html#%s', '')
extlinks['ctan'] =  (
    'https://ctan.org/pkg/%s', 'CTAN: ')

extensions = [
    'sphinx.ext.imgmath',
    'sphinx.ext.extlinks',
    'sphinx.ext.viewcode',
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "pallets_sphinx_themes",
    "sphinx_issues", # https://github.com/sloria/sphinx-issues/blob/master/README.rst
    "sphinxcontrib.jinja",  # https://github.com/tardyp/sphinx-jinja
    "sphinxcontrib.programoutput",  # https://github.com/NextThought/sphinxcontrib-programoutput
    'linuxdoc.rstFlatTable',    # Implementation of the 'flat-table' reST-directive.
    'linuxdoc.kfigure',         # Sphinx extension which implements scalable image handling.
    "sphinx_tabs.tabs", # https://github.com/djungelorm/sphinx-tabs
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "flask": ("https://flask.palletsprojects.com/", None),
    # "werkzeug": ("https://werkzeug.palletsprojects.com/", None),
    "jinja": ("https://jinja.palletsprojects.com/", None),
    "linuxdoc" : ("https://return42.github.io/linuxdoc/", None),
    "sphinx" : ("https://www.sphinx-doc.org/en/master/", None),
}

issues_github_path = "asciimoo/searx"

# HTML -----------------------------------------------------------------

sys.path.append(os.path.abspath('_themes'))
html_theme_path = ['_themes']
html_theme = "searx"

# sphinx.ext.imgmath setup
html_math_renderer = 'imgmath'
imgmath_image_format = 'svg'
imgmath_font_size = 14
# sphinx.ext.imgmath setup END

html_theme_options = {"index_sidebar_logo": True}
html_context = {
    "project_links": [
        ProjectLink("Source", GIT_URL),
        ProjectLink("Wiki", "https://github.com/asciimoo/searx/wiki"),
        ProjectLink("Public instances", "https://searx.space/"),
        ProjectLink("Twitter", "https://twitter.com/Searx_engine"),
    ]
}
html_sidebars = {
    "**": ["project.html", "relations.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}
html_static_path = ["static"]
html_logo = "static/img/searx_logo_small.png"
html_title = "Searx Documentation ({})".format("Searx-{}.tex".format(VERSION_STRING))
html_show_sourcelink = False

# LaTeX ----------------------------------------------------------------

latex_documents = [
    (master_doc, "searx-{}.tex".format(VERSION_STRING), html_title, author, "manual")
]
