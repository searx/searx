# -*- coding: utf-8 -*-

import  sys, os
from searx.version import VERSION_STRING
from pallets_sphinx_themes import ProjectLink

# Project --------------------------------------------------------------

project = u'searx'
copyright = u'2015-2019, Adam Tauber, Noémi Ványi'
author = u'Adam Tauber'
release, version = VERSION_STRING, VERSION_STRING

# General --------------------------------------------------------------

master_doc = "index"
source_suffix = '.rst'

extensions = [
    'sphinx.ext.viewcode',
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "pallets_sphinx_themes",
    "sphinx_issues", # https://github.com/sloria/sphinx-issues/blob/master/README.rst
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    # "flask": ("https://flask.palletsprojects.com/", None),
    # "werkzeug": ("https://werkzeug.palletsprojects.com/", None),
    # "jinja": ("https://jinja.palletsprojects.com/", None),
}

issues_github_path = "asciimoo/searx"

# HTML -----------------------------------------------------------------

sys.path.append(os.path.abspath('_themes'))

html_theme_path = ['_themes']
html_theme = "searx"

html_theme_options = {"index_sidebar_logo": True}
html_context = {
    "project_links": [
        ProjectLink("Source", os.environ.get("GIT_URL", "https://github.com/asciimoo")),
        ProjectLink("Wiki", "https://github.com/asciimoo/searx/wiki"),
        ProjectLink("Public instances", "https://github.com/asciimoo/searx/wiki/Searx-instances"),
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
