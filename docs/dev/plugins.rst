.. _dev plugin:

=======
Plugins
=======

.. sidebar:: Further reading ..

   - :ref:`plugins generic`

Plugins can extend or replace functionality of various components of searx.

Example plugin
==============

.. code:: python

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

External plugins
================

External plugins are standard python modules implementing all the requirements of the standard plugins.
Plugins can be enabled by adding them to :ref:`settings.yml`'s ``plugins`` section.
Example external plugin can be found `here <https://github.com/asciimoo/searx_external_plugin_example>`_.

Register your plugin
====================

To enable your plugin register your plugin in
searx > plugin > __init__.py.
And at the bottom of the file add your plugin like.
``plugins.register(name_of_python_file)``

Plugin entry points
===================

Entry points (hooks) define when a plugin runs. Right now only three hooks are
implemented. So feel free to implement a hook if it fits the behaviour of your
plugin.

Pre search hook
---------------

Runs BEFORE the search request. Function to implement: ``pre_search``

Post search hook
----------------

Runs AFTER the search request. Function to implement: ``post_search``

Result hook
-----------

Runs when a new result is added to the result list. Function to implement:
``on_result``
