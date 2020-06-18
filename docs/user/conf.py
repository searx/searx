# -*- coding: utf-8; mode: python -*-
"""Configuration for the Searx user handbook
"""
project   = 'Searx User-HB'
version   = release = VERSION_STRING

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ('index'                       # startdocname
     , 'searx-user-hb.tex'         # targetname
     , ''                          # take title from .rst
     , author                      # author
     , 'howto'                     # documentclass
     , False                       # toctree_only
    ),
]

