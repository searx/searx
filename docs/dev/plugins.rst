.. _dev plugin:

=======
Plugins
=======

.. sidebar:: Further reading ..

   - :ref:`plugins generic`

Plugins can extend or replace functionality of various components of searx.
To create a plugin put your python file in searx > plugins.

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

Register your plugin
====================

To enable your plugin register your plugin in
searx > plugin > __init__.py.
And at the bottom of the file add your plugin like.
``plugins.register(name_of_python_file)``

Plugin entry points
===================

Entry points (hooks) define when a plugin runs. Right now only four hooks are
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

Custom search hook
------------------

Runs AFTER the search request. Function to implement:
``custom_results``

If none of the above hooks fit your needs you can use the following hook. **This is to be used carefully.**
With this hook you can return a custom flask response you would return in a a regular flask application
(see flask documentation for all the available options). The functions needs to accept 2 parameters.

1. Search obj which is of type raw. Get the the query with search_obj.query
2. Will be of type request (flask)

If your function did nothing should return None so the normal search continues.

Example can be found in searx > plugins > bangs.py

