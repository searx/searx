searx
=====

A privacy-respecting, hackable [metasearch engine](https://en.wikipedia.org/wiki/Metasearch_engine).

List of [running instances](https://github.com/asciimoo/searx/wiki/Searx-instances).

[![Flattr searx](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=asciimoo&url=https://github.com/asciimoo/searx&title=searx&language=&tags=github&category=software)

### Features

* Tracking free
* Modular (see [examples](https://github.com/asciimoo/searx/blob/master/examples))
* Parallel queries
* Supports json output `curl https://searx.0x2a.tk/?format=json&q=[query]`
* Opensearch support (you can set as default search engine in your browser)
* Search categories
* User-agent forwarding

### Installation

* clone source: `git clone git@github.com:asciimoo/searx.git && cd searx`
* install dependencies: `pip install -r requirements.txt`
* edit your [searx/settings.py](https://github.com/asciimoo/searx/blob/master/searx/settings.py) (set your `secret_key`!)
* rename `engines.cfg_sample` to `engines.cfg`
* run `python searx/webapp.py` to start the application

### TODO

* Moar engines
* Better ui
* Language support
* Documentation
* Pagination
* Search suggestions
* Tests


### Bugs

Bugs or suggestions? Visit the [issue tracker](https://github.com/asciimoo/searx/issues).

