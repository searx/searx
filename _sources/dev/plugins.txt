Plugins
-------

Plugins can extend/replace functionality of various components inside
searx.

example\_plugin.py
~~~~~~~~~~~~~~~~~~

.. code:: python

    name = 'Example plugin'
    description = 'This plugin extends the suggestions with the word "example"'
    default_on = False  # disable by default

    js_dependencies = tuple()  # optional, list of static js files
    css_dependencies = tuple()  # optional, list of static css files


    # attach callback to the post search hook
    #  request: flask request object
    #  ctx: the whole local context of the post search hook
    def post_search(request, ctx):
        ctx['search'].suggestions.add('example')
        return True

Currently implemented plugin entry points (a.k.a hooks)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Pre search hook (``pre_search``)
-  Post search hook (``post_search``)
-  Result hook (``on_result``) (is called if a new result is added (see
   https\_rewrite plugin))

Feel free to add more hooks to the code if it is required by a plugin.

TODO
~~~~

-  Better documentation
-  More hooks
-  search hook (is called while searx is requesting results (for
   example: things like math-solver), the different hooks are running
   parallel)

