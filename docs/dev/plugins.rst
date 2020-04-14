.. _dev plugin:

========================
Developing searx plugins
========================

.. sidebar:: Further reading ..

   - :ref:`plugins generic`

Plugins can extend or replace functionality of various components of searx.  A
Plugin consists of :py:obj:`required <searx.plugins.required_attrs>` and
:py:obj:`optional <searx.plugins.optional_attrs>` attributes and it adds
*callbacks* to hooks.  Hooks define when a plugin runs.

- Pre search hook: :py:obj:`pre_search <searx.plugins.Plugin.pre_search>`
- Post search hook: :py:obj:`post_search <searx.plugins.Plugin.post_search>`
- On result is added: :py:obj:`on_result <searx.plugins.Plugin.on_result>`

Right now only three hooks are implemented.  So feel free to implement a hook
if it fits the behaviour of your plugin.  For details see :ref:`Example plugin`
and read :ref:`searx.plugins sources`.

.. _Example plugin:

.. code-block:: python
   :caption: Example plugin

   name = 'Example plugin'
   description = 'This plugin extends the suggestions with the word "example"'
   default_on = False  # disabled by default

   js_dependencies = tuple()  # optional, list of static js files
   css_dependencies = tuple()  # optional, list of static css files


   # attach callback to the post search hook
   #  request: flask request object
   #  ctx: the whole local context of the post search hook
   def post_search(request, ctx):
       ctx['search'].suggestions.add('example')
       return True

.. _searx.plugins sources:

Remarks from source code
========================

.. automodule:: searx.plugins
   :members:
