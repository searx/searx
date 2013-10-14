searx
=====

Minimalist web interface to different search engines.

### Features

* Tracking free (no javascript, no cookies)
* Modular
* Parallel queries

### Installation

*   install dependencies: `pip install -r requirements.txt`
*   clone source: `git clone git@github.com:asciimoo/searx.git && cd searx`
*   create a config file: `cp searx.conf_sample search.conf`
*   edit your config (set your `secret_key`!)
*   run `python searx/webapp.py` to start the application
