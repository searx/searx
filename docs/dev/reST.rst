.. _reST primer:

===========
reST primer
===========

.. sidebar:: KISS_ and readability_

   Instead of defining more and more roles, we at searx encourage our
   contributors to follow principles like KISS_ and readability_.

We at searx are using reStructuredText (aka reST_) markup for all kind of
documentation, with the builders from the Sphinx_ project a HTML output is
generated and deployed at :docs:`github.io <.>`.

The sources of Searx's documentation are located at :origin:`docs`.  Run
:ref:`make docs-live <make docs-live>` to build HTML while editing.

------

.. contents:: Contents
   :depth: 3
   :local:
   :backlinks: entry

Sphinx_ and reST_ have their place in the python ecosystem.  Over that reST is
used in popular projects, e.g the Linux kernel documentation `[kernel doc]`_.

.. _[kernel doc]: https://www.kernel.org/doc/html/latest/doc-guide/sphinx.html

.. sidebar:: Content matters

   The readability_ of the reST sources has its value, therefore we recommend to
   make sparse usage of reST markup / .. content matters!

**reST** is a plaintext markup language, its markup is *mostly* intuitive and
you will not need to learn much to produce well formed articles with.  I use the
word *mostly*: like everything in live, reST has its advantages and
disadvantages, some markups feel a bit grumpy (especially if you are used to
other plaintext markups).

Soft skills
===========

Before going any deeper into the markup let's face on some **soft skills** a
trained author brings with, to reach a well feedback from readers:

- Documentation is dedicated to an audience and answers questions from the
  audience point of view.
- Don't detail things which are general knowledge from the audience point of
  view.
- Limit the subject, use cross links for any further reading.

To be more concrete what a *point of view* means.  In the (:origin:`docs`)
folder we have three sections (and the *blog* folder), each dedicate to a
different group of audience.

.. sidebar:: Further reading

   - Sphinx-Primer_
   - `Sphinx markup constructs`_
   - reST_, docutils_, `docutils FAQ`_
   - Sphinx_, `sphinx-doc FAQ`_
   - `sphinx config`_, doctree_
   - `sphinx cross references`_
   - intersphinx_
   - `Sphinx's autodoc`_
   - `Sphinx's Python domain`_, `Sphinx's C domain`_

User's POV: :origin:`docs/user`
  A typical user knows about search engines and might have heard about
  meta crawlers and privacy.

Admin's POV: :origin:`docs/admin`
  A typical Admin knows about setting up services on a linux system, but he does
  not know all the pros and cons of a searx setup.

Developer's POV: :origin:`docs/dev`
  Depending on the readability_ of code, a typical developer is able to read and
  understand source code.  Describe what a item aims to do (e.g. a function),
  describe chronological order matters, describe it.  Name the *out-of-limits
  condition* and all the side effects a external developer will not know.

.. _reST inline markup:

Basic inline markup
===================

``*italics*`` -- *italics*
  one asterisk for emphasis

``**boldface**`` -- **boldface**
  two asterisks for strong emphasis and

````foo()```` -- ``foo()``
  backquotes for code samples and literals.

``\*foo is a pointer`` -- \*foo is a pointer
  If asterisks or backquotes appear in running text and could be confused with
  inline markup delimiters, they have to be escaped with a backslash (``\*foo is
  a pointer``).


Roles
=====

A *custom interpreted text role* (:duref:`ref <roles>`) is an inline piece of
explicit markup.  It signifies that that the enclosed text should be interpreted
in a specific way.  The general syntax is ``:rolename:`content```.

Docutils supports the following roles:

* :durole:`emphasis` -- equivalent of ``*emphasis*``
* :durole:`strong` -- equivalent of ``**strong**``
* :durole:`literal` -- equivalent of ````literal````
* :durole:`subscript` -- subscript text
* :durole:`superscript` -- superscript text
* :durole:`title-reference` -- for titles of books, periodicals, and other
  materials

Refer to `Sphinx Roles`_ for roles added by Sphinx.


Anchors & Links
===============

.. _reST anchor:

Anchors
-------

.. _ref role:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-ref

To refer a point in the documentation a anchor is needed.  The :ref:`reST
template <reST template>` shows an example where a chapter titled *"Chapters"*
gets an anchor named ``chapter title``.  Another example from *this* document,
where the anchor named ``reST anchor``:

.. code:: reST

   .. _reST anchor:

   Anchors
   -------

   To refer a point in the documentation a anchor is needed ...

To refer anchors use the `ref role`_ markup:

.. code:: reST

   Visit chapter :ref:`reST anchor`.
   Or set hyperlink text manualy :ref:`foo bar <reST anchor>`.

.. admonition:: ``:ref:`` role
   :class: rst-example

   Visist chapter :ref:`reST anchor`
   Or set hyperlink text manualy :ref:`foo bar <reST anchor>`.

.. _reST ordinary ref:

link ordinary URL
-----------------

If you need to reference external URLs use *named* hyperlinks to maintain
readability of reST sources.  Here is a example taken from *this* article:

.. code:: reST

   .. _Sphinx Field Lists:
      https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html

   With the *named* hyperlink `Sphinx Field Lists`_, the raw text is much more
   readable.

   And this shows the alternative (less readable) hyperlink markup `Sphinx Field
   Lists
   <https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html>`__.

.. admonition:: Named hyperlink
   :class: rst-example

   With the *named* hyperlink `Sphinx Field Lists`_, the raw text is much more
   readable.

   And this shows the alternative (less readable) hyperlink markup `Sphinx Field
   Lists
   <https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html>`__.


.. _reST smart ref:

smart references
----------------

With the power of sphinx.ext.extlinks_ and intersphinx_ referencing external
content becomes smart. To refer ...

sphinx.ext.extlinks_:

:project's wiki article:          :wiki:`Searx-instances`
:to docs public URL:              :docs:`dev/reST.html`
:files & folders from origin:     :origin:`docs/dev/reST.rst`
:a pull request:                  :pull:`1756`
:a patch:                         :patch:`af2cae6`
:a PyPi package:                  :pypi:`searx`
:a manual page man:               :man:`bash`

.. code:: reST

   :project's wiki article:          :wiki:`Searx-instances`
   :to docs public URL:              :docs:`dev/reST.html`
   :files & folders from origin:     :origin:`docs/dev/reST.rst`
   :a pull request:                  :pull:`1756`
   :a patch:                         :patch:`af2cae6`
   :a PyPi package:                  :pypi:`searx`
   :a manual page man:               :man:`bash`


intersphinx_:

   :external anchor:                 :ref:`python:and`
   :external doc anchor:             :doc:`jinja:templates`
   :python code object:              :py:obj:`datetime.datetime`
   :flask code object:               webapp is a :py:obj:`flask.Flask` app

.. code:: reST

   :external anchor:                 :ref:`python:and`
   :external doc anchor:             :doc:`jinja:templates`
   :python code object:              :py:obj:`datetime.datetime`
   :flask code object:               webapp is a :py:obj:`flask.Flask` app


Intersphinx is configured in :origin:`docs/conf.py`:

.. code:: python

    intersphinx_mapping = {
        "python": ("https://docs.python.org/3/", None),
        "flask": ("https://flask.palletsprojects.com/", None),
	"jinja": ("https://jinja.palletsprojects.com/", None),
    }


To list all anchors of the inventory (e.g. ``python``) use:

.. code:: sh

   $ python -m sphinx.ext.intersphinx https://docs.python.org/3/objects.inv


.. _reST basic structure:

Basic article structure
=======================

The basic structure of an article makes use of heading adornments to markup
chapter, sections and subsections.

#. ``=`` with overline for document title
#. ``=`` for chapters
#. ``-`` for sections
#. ``~`` for subsections

.. _reST template:

.. admonition:: reST template
   :class: rst-example

   .. code:: reST

       .. _document title:

       ==============
       Document title
       ==============

       Lorem ipsum dolor sit amet, consectetur adipisici elit ..
       Further read :ref:`chapter title`.

       .. _chapter title:

       Chapters
       ========

       Ut enim ad minim veniam, quis nostrud exercitation ullamco
       laboris nisi ut aliquid ex ea commodi consequat ...

       Section
       -------

       lorem ..

       Subsection
       ~~~~~~~~~~

       lorem ..

.. _reST lists:

List markups
============

Bullet list
-----------

List markup (:duref:`ref <bullet-lists>`) is simple:

.. code:: reST

   - This is a bulleted list.

     1. Nested lists are possible, but be aware that they must be separated from
        the parent list items by blank line
     2. Second item of nested list

   - It has two items, the second
     item uses two lines.

   #. This is a numbered list.
   #. It has two items too.

.. admonition:: bullet list
   :class: rst-example

   - This is a bulleted list.

     1. Nested lists are possible, but be aware that they must be separated from
        the parent list items by blank line
     2. Second item of nested list

   - It has two items, the second
     item uses two lines.

   #. This is a numbered list.
   #. It has two items too.


Definition list
---------------

.. sidebar:: definition term

   Note that the term cannot have more than one line of text.

Definition lists (:duref:`ref <definition-lists>`) are created as follows:

.. code:: reST

   term (up to a line of text)
      Definition of the term, which must be indented

      and can even consist of multiple paragraphs

   next term
      Description.

.. admonition:: definition list
   :class: rst-example

   term (up to a line of text)
      Definition of the term, which must be indented

      and can even consist of multiple paragraphs

   next term
      Description.


Quoted paragraphs
-----------------

Quoted paragraphs (:duref:`ref <block-quotes>`) are created by just indenting
them more than the surrounding paragraphs.  Line blocks (:duref:`ref
<line-blocks>`) are a way of preserving line breaks:

.. code:: reST

   normal paragraph ...
   lorem ipsum.

      Quoted paragraph ...
      lorem ipsum.

   | These lines are
   | broken exactly like in
   | the source file.


.. admonition:: Quoted paragraph and line block
   :class: rst-example

   normal paragraph ...
   lorem ipsum.

      Quoted paragraph ...
      lorem ipsum.

   | These lines are
   | broken exactly like in
   | the source file.


.. _reST field list:

Field Lists
-----------

.. _Sphinx Field Lists:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html

.. sidebar::  bibliographic fields

   First lines fields are bibliographic fields, see `Sphinx Field Lists`_.

Field lists are used as part of an extension syntax, such as options for
directives, or database-like records meant for further processing.  Field lists
are mappings from field names to field bodies.  They marked up like this:

.. code:: reST

   :fieldname: Field content
   :foo:       first paragraph in field foo

	       second paragraph in field foo

   :bar:       Field content

.. admonition:: Field List
   :class: rst-example

   :fieldname: Field content
   :foo:       first paragraph in field foo

	       second paragraph in field foo

   :bar:       Field content


They are commonly used in Python documentation:

.. code:: python

   def my_function(my_arg, my_other_arg):
       """A function just for me.

       :param my_arg: The first of my arguments.
       :param my_other_arg: The second of my arguments.

       :returns: A message (just for me, of course).
       """

Further list blocks
-------------------

- field lists (:duref:`ref <field-lists>`, with caveats noted in
  :ref:`reST field list`)
- option lists (:duref:`ref <option-lists>`)
- quoted literal blocks (:duref:`ref <quoted-literal-blocks>`)
- doctest blocks (:duref:`ref <doctest-blocks>`)


.. _KISS: https://en.wikipedia.org/wiki/KISS_principle
.. _readability: https://docs.python-guide.org/writing/style/
.. _Sphinx-Primer:
    http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _reST: https://docutils.sourceforge.io/rst.html
.. _Sphinx Roles:
    https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html
.. _Sphinx: http://www.sphinx-doc.org
.. _`sphinx-doc FAQ`: http://www.sphinx-doc.org/en/stable/faq.html
.. _Sphinx markup constructs:
    http://www.sphinx-doc.org/en/stable/markup/index.html
.. _`sphinx cross references`:
    http://www.sphinx-doc.org/en/stable/markup/inline.html#cross-referencing-arbitrary-locations
.. _sphinx.ext.extlinks:
    https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html
.. _intersphinx: http://www.sphinx-doc.org/en/stable/ext/intersphinx.html
.. _sphinx config: http://www.sphinx-doc.org/en/stable/config.html
.. _Sphinx's autodoc: http://www.sphinx-doc.org/en/stable/ext/autodoc.html
.. _Sphinx's Python domain:
    http://www.sphinx-doc.org/en/stable/domains.html#the-python-domain
.. _Sphinx's C domain:
   http://www.sphinx-doc.org/en/stable/domains.html#cross-referencing-c-constructs
.. _doctree:
    http://www.sphinx-doc.org/en/master/extdev/tutorial.html?highlight=doctree#build-phases
.. _docutils: http://docutils.sourceforge.net/docs/index.html
.. _docutils FAQ: http://docutils.sourceforge.net/FAQ.html
