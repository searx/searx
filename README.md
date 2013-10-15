searx
=====

Minimalist web interface to different search engines.

### Features

* Tracking free (no javascript)
* Modular (see [examples](https://github.com/asciimoo/searx/blob/master/examples))
* Parallel queries

### Installation

*   install dependencies: `pip install -r requirements.txt`
*   clone source: `git clone git@github.com:asciimoo/searx.git && cd searx`
*   create a config file: `cp searx.conf_sample search.conf`
*   edit your config (set your `secret_key`!)
*   run `python searx/webapp.py` to start the application
