.. _engines generic:

=======
engines
=======

.. sidebar:: Further reading ..

   - :ref:`engines generic`
   - :ref:`configured engines`
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
Suspend end   **SE**
------------- ----------- ---------------------------------
Safe search   **SS**
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
        - SE

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
        - {{mod.suspend_end_time}}

     {% endfor %}
