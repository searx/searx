.. _adminapi:

Administration API
------------------

Get configuration data
~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

    GET /config

Sample response
```````````````

.. code:: sh
    
    {
      "autocomplete": "", 
      "categories": [
        "map", 
        "it", 
        "images", 
      ], 
      "default_locale": "", 
      "default_theme": "oscar", 
      "engines": [
        {
          "categories": [
            "map"
          ], 
          "enabled": true, 
          "name": "openstreetmap", 
          "shortcut": "osm"
        }, 
        {
          "categories": [
            "it"
          ], 
          "enabled": true, 
          "name": "arch linux wiki", 
          "shortcut": "al"
        }, 
        {
          "categories": [
            "images"
          ], 
          "enabled": true, 
          "name": "google images", 
          "shortcut": "goi"
        }, 
        {
          "categories": [
            "it"
          ], 
          "enabled": false, 
          "name": "bitbucket", 
          "shortcut": "bb"
        }, 
      ], 
      "instance_name": "searx", 
      "locales": {
        "de": "Deutsch (German)", 
        "en": "English", 
        "eo": "Esperanto (Esperanto)", 
      }, 
      "plugins": [
        {
          "enabled": true, 
          "name": "HTTPS rewrite"
        }, 
        {
          "enabled": false, 
          "name": "Vim-like hotkeys"
        }
      ], 
      "safe_search": 0
    }
