Search syntax
=============

Searx allows you to modify the default categories, engines and search
language via the search query.

Category/engine prefix: ``!``

Language prefix: ``:``

Prefix to add engines and categories to the currently selected
categories: ``?``

Abbrevations of the engines and languages are also accepted.
Engine/category modifiers are chainable and inclusive (e.g. with
`!it !ddg !wp qwer <https://searx.me/?q=%21it%20%21ddg%20%21wp%20qwer>`_
search in IT category **and** duckduckgo **and** wikipedia for ``qwer``).

See the `/preferences page <https://searx.me/preferences>`_ for the
list of engines, categories and languages.

Examples
~~~~~~~~

Search in wikipedia for ``qwer``:
`!wp qwer <https://searx.me/?q=%21wp%20qwer>`__ or
`!wikipedia qwer <https://searx.me/?q=%21wikipedia%20qwer>`_

Image search:
`!images Cthulhu <https://searx.me/?q=%21images%20Cthulhu>`_

Custom language in wikipedia:
`:hu !wp hackerspace <https://searx.me/?q=%3Ahu%20%21wp%20hackerspace>`_
