Plugins
-------

Plugins can extend or replace functionality of various components of
searx.

Example plugin
~~~~~~~~~~~~~~

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

Plugin entry points
~~~~~~~~~~~~~~~~~~~

Entry points (hooks) define when a plugin runs. Right now only three hooks are implemented. So feel free to implement a hook if it fits the behaviour of your plugin.

Pre search hook
```````````````

Runs BEFORE the search request. Function to implement: ``pre_search``

Post search hook
````````````````

Runs AFTER the search request. Function to implement: ``post_search``

Result hook
```````````

Runs when a new result is added to the result list. Function to implement: ``on_result``
