.. _dev plugin:

========================
Developing searx plugins
========================

.. _Using package metadata:
    https://packaging.python.org/guides/creating-and-discovering-plugins/#using-package-metadata

.. sidebar:: Further reading ..

   - :ref:`plugins generic`

Plugins can extend or replace functionality of various components of searx.  A
Plugin consists of :py:obj:`required <searx.plugins.required_attrs>` and
:py:obj:`optional <searx.plugins.optional_attrs>` attributes and it adds
*callbacks* to hooks.  Hooks define when a plugin runs. Right now only three
hooks are implemented :ref:`[ref] <searx.plugins sources>`:

- Pre search hook: :py:func:`pre_search() <searx.plugins.Plugin.pre_search>`
- Post search hook: :py:func:`post_search() <searx.plugins.Plugin.post_search>`
- On result is added: :py:func:`on_result() <searx.plugins.Plugin.on_result>`

You can create a plugin on a *module level* -- like shown in :ref:`Example
plugin` -- or by subclassing :py:class:`searx.plugins.Plugin` .

.. _Example plugin:

.. code-block:: python
   :caption: Example plugin

   name = 'Example plugin'
   description = 'This plugin extends the suggestions with the word "example"'
   default_on = False  # disabled by default

   js_dependencies = tuple()   # optional, list of static JS files
   css_dependencies = tuple()  # optional, list of static CSS files


   # attach callback to the post search hook
   #  request: flask request object
   #  ctx: the whole local context of the post search hook
   def post_search(request, ctx):
       ctx['search'].suggestions.add('example')
       return True

Searx discovers *external* plugins by `Using package metadata`_.  Add a
:py:obj:`'searx.plugins' <searx.plugins.ENTRY_POINTS>` item to the
``entry_points`` argument in you project's ``setup.py`` -- like shown in
:ref:`setup.py <plugin register entry_point>`.

.. _plugin register entry_point:

.. code-block:: python
   :caption: ``setup.py`` -- register plugin using ``entry_points`` argument.

   setup(
       name = 'example',
       # ...
       entry_points = {
           'searx.plugins': [ 'foo_example_plugin = foo.example.plugin', ],
       },
   )

.. _external plugins:

Known plugins from the Web
==========================

tgwf-searx-plugins
  Any results not being hosted on green infrastructure will be filtered (origin
  `PR1878 <https://github.com/asciimoo/searx/pull/1878>`_)::

    pip install git+https://github.com/return42/tgwf-searx-plugins


.. _searx.plugins sources:

Remarks from source code
========================

.. automodule:: searx.plugins
   :members:
