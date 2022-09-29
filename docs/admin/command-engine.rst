=====================================
Run shell commands from your instance
=====================================

Command line engines are custom engines that run commands in the shell of the
host. In this article you can learn how to create a command engine and how to
customize the result display.

The command
===========

When specifyng commands, you must make sure the commands are available on the
searx host. Searx will not install anything for you. Also, make sure that the
``searx`` user on your host is allowed to run the selected command and has
access to the required files.

Access control
==============

Be careful when creating command engines if you are running a public
instance. Do not expose any sensitive information. You can restrict access by
configuring a list of access tokens under tokens in your ``settings.yml``.

Available settings
==================

* ``command``: A comma separated list of the elements of the command. A special
  token ``{{QUERY}}`` tells searx where to put the search terms of the
  user. Example: ``['ls', '-l', '-h', '{{QUERY}}']``
* ``query_type``: The expected type of user search terms. Possible values:
  ``path`` and ``enum``. ``path`` checks if the uesr provided path is inside the
  working directory. If not the query is not executed. ``enum`` is a list of
  allowed search terms. If the user submits something which is not included in
  the list, the query returns an error.
* ``delimiter``: A dict containing a delimiter char and the "titles" of each
  element in keys.
* ``parse_regex``: A dict containing the regular expressions for each result
  key.
* ``query_enum``: A list containing allowed search terms if ``query_type`` is
  set to ``enum``.
* ``working_dir``: The directory where the command has to be executed. Default:
  ``.``
* ``result_separator``: The character that separates results. Default: ``\n``

Customize the result template
=============================

There is a default result template for displaying key-value pairs coming from
command engines. If you want something more tailored to your result types, you
can design your own template.

Searx relies on `Jinja2 <https://jinja.palletsprojects.com/>`_ for
templating. If you are familiar with Jinja, you will not have any issues
creating templates. You can access the result attributes with ``{{
result.attribute_name }}``.

In the example below the result has two attributes: ``header`` and ``content``.
To customize their diplay, you need the following template (you must define
these classes yourself):

.. code:: html

    <div class="result">
        <div class="result-header">
            {{ result.header }}
        </div>
        <div class="result-content">
            {{ result.content }}
        </div>
    </div>

Then put your template under ``searx/templates/{theme-name}/result_templates``
named ``your-template-name.html``. You can select your custom template with the
option ``result_template``.

.. code:: yaml

  - name: your engine name
    engine: command
    result_template: your-template-name.html

Examples
========

Find files by name
------------------

The first example is to find files on your searx host. It uses the command
`find` available on most Linux distributions. It expects a path type query. The
path in the search request must be inside the ``working_dir``.

The results are displayed with the default `key-value.html` template.  A result
is displayed in a single row table with the key "line".

.. code:: yaml

  - name : find
    engine : command
    command : ['find', '.', '-name', '{{QUERY}}']
    query_type : path
    shortcut : fnd
    tokens : []
    disabled : True
    delimiter :
        chars : ' '
        keys : ['line']


Find files by contents
-----------------------

In the second example, we define an engine that searches in the contents of the
files under the ``working_dir``. The search type is not defined, so the user can
input any string they want. To restrict the input, you can set the ``query_type``
to ``enum`` and only allow a set of search terms to protect
yourself. Alternatively, make the engine private, so no one malevolent accesses
the engine.

.. code:: yaml

  - name : regex search in files
    engine : command
    command : ['grep', '{{QUERY}}']
    shortcut : gr
    tokens : []
    disabled : True
    delimiter :
        chars : ' '
        keys : ['line']
