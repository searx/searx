searx
=====

A privacy-respecting, hackable [metasearch engine](https://en.wikipedia.org/wiki/Metasearch_engine).

List of [running instances](https://github.com/asciimoo/searx/wiki/Searx-instances).

[![Flattr searx](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=asciimoo&url=https://github.com/asciimoo/searx&title=searx&language=&tags=github&category=software)

### Features

* Tracking free
* Modular (see [examples](https://github.com/asciimoo/searx/blob/master/examples))
* Parallel queries
* Supports multiple output formats
 * json `curl https://searx.0x2a.tk/?format=json&q=[query]`
 * csv `curl https://searx.0x2a.tk/?format=csv&q=[query]`
 * opensearch/rss `curl https://searx.0x2a.tk/?format=rss&q=[query]`
* Opensearch support (you can set as default search engine)
* Configurable search engines/categories

### Installation

* clone source: `git clone git@github.com:asciimoo/searx.git && cd searx`
* install dependencies: `pip install -r requirements.txt`
* edit your [searx/settings.py](https://github.com/asciimoo/searx/blob/master/searx/settings.py) (set your `secret_key`!)
* rename `engines.cfg_sample` to `engines.cfg`
* run `python searx/webapp.py` to start the application

For all the details, follow this [step by step installation](https://github.com/asciimoo/searx/wiki/Installation)

### Alternative (Recommended) Installation

* clone source: `git clone git@github.com:asciimoo/searx.git && cd searx`
* build in current folder: `make minimal`
* run `bin/searx-run` to start the application


### Development

Just run `make`. Versions of dependencies are pinned down inside `versions.cfg` to produce most stable build.

#### Command make

##### `make`

Builds development environment with testing support.

##### `make tests`

Runs tests. You can write tests [here](https://github.com/asciimoo/searx/tree/master/searx/tests) and remember 'untested code is broken code'.

##### `make robot`

Runs robot (Selenium) tests, you must have `firefox` installed because this functional tests actually run the browser and perform operations on it. Also searx is executed with [settings_robot](https://github.com/asciimoo/searx/blob/master/searx/settings_robot.py).

##### `make flake8`

'pep8 is a tool to check your Python code against some of the style conventions in [PEP 8](http://www.python.org/dev/peps/pep-0008/).'

##### `make coverage`

Checks coverage of tests, after running this, execute this: `firefox ./coverage/index.html`

##### `make minimal`

Used to make co-called production environment - without tests (you should ran tests before deploying searx on the server).

##### `make clean`

Deletes several folders and files (see `Makefile` for more), so that next time you run any other `make` command it will rebuild everithing.


### TODO

* Moar engines
* Better ui
* Language support
* Documentation
* Pagination
* Fix `flake8` errors, `make flake8` will be merged into `make tests` when it does not fail anymore
* Tests
* When we have more tests, we can integrate Travis-CI


### Bugs

Bugs or suggestions? Visit the [issue tracker](https://github.com/asciimoo/searx/issues).


### [License](https://github.com/asciimoo/searx/blob/master/LICENSE)


### More about searx

* [ohloh](https://www.ohloh.net/p/searx/)
* [twitter](https://twitter.com/Searx_engine)

