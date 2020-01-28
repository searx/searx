.. _engines generic:

=======
Engines
=======

.. sidebar:: Further reading ..

   - :ref:`settings engine`
   - :ref:`engine settings`
   - :ref:`engine file`

============= =========== ==================== ============
:ref:`engine settings`    :ref:`engine file`
------------------------- ---------------------------------
Name (cfg)                Categories
------------------------- ---------------------------------
Engine        ..          Paging support       **P**
------------------------- -------------------- ------------
Shortcut      **S**       Language support     **L**
Timeout       **TO**      Time range support   **TR**
Disabled      **D**       Offline              **O**
------------- ----------- -------------------- ------------
Safe search   **SS**
------------- ----------- ---------------------------------
Weigth        **W**
------------- ----------- ---------------------------------
Disabled      **D**
============= =========== =================================

Configuration defaults (at built time):

.. _configured engines:

.. jinja:: webapp

   .. flat-table:: Engines configured at built time (defaults)
      :header-rows: 1
      :stub-columns: 2

      * - Name (cfg)
        - S
        - Engine
        - TO
        - Categories
        - P
        - L
        - SS
        - D
        - TR
        - O
	- W
	- D

      {% for name, mod in engines.items() %}

      * - {{name}}
        - !{{mod.shortcut}}
        - {{mod.__name__}}
        - {{mod.timeout}}
        - {{", ".join(mod.categories)}}
        - {{(mod.paging and "y") or ""}}
        - {{(mod.language_support and "y") or ""}}
        - {{(mod.safesearch and "y") or ""}}
        - {{(mod.disabled and "y") or ""}}
        - {{(mod.time_range_support and "y") or ""}}
        - {{(mod.offline and "y") or ""}}
        - {{mod.weight or 1 }}
        - {{(mod.disabled and "y") or ""}}

     {% endfor %}
