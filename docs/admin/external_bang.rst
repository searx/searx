.. _external bang:

=============
External bang
=============

*External Bangs* are shortcuts that quickly take you to search results on other
sites.

List of available *bangs*:

.. _bang list:

.. jinja:: external_bang

   .. flat-table:: List of available *bangs*
      :header-rows: 1
      :stub-columns: 1

      * - Name
        - !!bang
        - regions

      {% for bang in bang_list %}

      * - {{bang['name']}}
        - !!{{', !!'.join(bang['triggers'])}}
        - {{', '.join(bang['regions'])}}

     {% endfor %}
