# -*- coding: utf-8; mode: makefile-gmake -*-
.DEFAULT_GOAL=help

export PY_ENV PYDIST PYBUILD

include utils/makefile.include

DOC       = docs
PYLINT_SEARX_DISABLE_OPTION := I,C,R,W0105,W0212,W0511,W0603,W0613,W0621,W0702,W0703,W1401,E1136
PYLINT_ADDITIONAL_BUILTINS_FOR_ENGINES := supported_languages,language_aliases

# python version to use
PY       ?=3
# $(PYTHON) points to the python interpreter from the OS!  The python from the
# OS is needed e.g. to create a virtualenv.  For tasks inside the virtualenv the
# interpeter from '$(PY_ENV_BIN)/python' is used.
PYTHON   ?= python$(PY)

VTENV_OPTS ?=

PY_ENV       = ./$(LXC_ENV_FOLDER)local/py$(PY)
PY_ENV_BIN   = $(PY_ENV)/bin
PY_ENV_ACT   = . $(PY_ENV_BIN)/activate

# folder where the python distribution takes place
PYDIST   = ./$(LXC_ENV_FOLDER)dist
# folder where the python intermediate build files take place
PYBUILD  = ./$(LXC_ENV_FOLDER)build


include utils/makefile.sphinx

all: clean install

PHONY += help-min help-all help

help: help-min
	@echo  ''
	@echo  'to get more help:  make help-all'

help-min:
	@echo  '  test        - run developer tests'
	@echo  '  docs        - build documentation'
	@echo  '  docs-live   - autobuild HTML documentation while editing'
	@echo  '  run         - run developer instance'
	@echo  '  install     - developer install (./local)'
	@echo  '  uninstall   - uninstall (./local)'
	@echo  '  pybuild     - build python packages ($(PYDIST) $(PYBUILD))'
	@echo  '  upload-pypi - upload $(PYDIST)/* files to PyPi'
	@echo  '  gh-pages    - build docs & deploy on gh-pages branch'
	@echo  '  clean       - drop builds and environments'
	@echo  '  pyclean     - clean intermediate python objects'
	@echo  '  project     - re-build generic files of the searx project'
	@echo  '  buildenv    - re-build environment files (aka brand)'
	@echo  '  themes      - re-build build the source of the themes'
	@echo  '  docker      - build Docker image'
	@echo  '  node.env    - download & install npm dependencies locally'
	@echo  ''
	@echo  'options:'
	@echo  '  make PY=3.7 [targets] => to eval targets with python 3.7 ($(PY))'
	@echo  ''
	@$(MAKE) -e -s make-help

help-all: help-min
	@echo  ''
	@$(MAKE) -e -s docs-help

PHONY += install
install: buildenv pyenvinstall

PHONY += uninstall
uninstall: pyenvuninstall

PHONY += clean
clean: pyclean docs-clean node.clean test.clean
	$(call cmd,common_clean)

PHONY += run
run:  buildenv pyenvinstall
	$(Q) ( \
	sleep 2 ; \
	xdg-open http://127.0.0.1:8888/ ; \
	) &
	SEARX_DEBUG=1 $(PY_ENV)/bin/python ./searx/webapp.py

# docs
# ----

sphinx-doc-prebuilds:: buildenv pyenvinstall prebuild-includes

PHONY += docs
docs:  sphinx-doc-prebuilds
	$(call cmd,sphinx,html,docs,docs)

PHONY += docs-live
docs-live:  sphinx-doc-prebuilds
	$(call cmd,sphinx_autobuild,html,docs,docs)

PHONY += docs-clean
docs-clean: $(BOOKS_CLEAN)
	$(call cmd,sphinx_clean)

PHONY += prebuild-includes
prebuild-includes:
	$(Q)mkdir -p $(DOCS_BUILD)/includes
	$(Q)./utils/searx.sh doc | cat > $(DOCS_BUILD)/includes/searx.rst
	$(Q)./utils/filtron.sh doc | cat > $(DOCS_BUILD)/includes/filtron.rst
	$(Q)./utils/morty.sh doc | cat > $(DOCS_BUILD)/includes/morty.rst


$(GH_PAGES)::
	@echo "doc available at --> $(DOCS_URL)"


# virutalenv setup
# ----------------

quiet_cmd_pyenv  = PYENV     usage: $ $(PY_ENV_ACT)
      cmd_pyenv  = \
	if [ -d "./$(PY_ENV)" -a -x "./$(PY_ENV_BIN)/python" ]; then \
		echo "PYENV     using virtualenv from $(PY_ENV)"; \
	else \
		rm -f $(PY_ENV)/requirements.sha256; \
		$(PYTHON) -m venv $(VTENV_OPTS) $(PY_ENV); \
	fi

quiet_cmd_pyenvinstall = PYENV     install $2
      cmd_pyenvinstall = \
	if cat $(PY_ENV)/requirements.sha256 2>/dev/null | sha256sum --check --status 2>/dev/null; then \
		echo "PYENV     already installed"; \
	else \
		rm -f $(PY_ENV)/requirements.sha256; \
		$(PY_ENV_ACT); \
		python -m pip install $(PIP_VERBOSE) -U pip wheel setuptools; \
		python -m pip install --use-feature=2020-resolver -r requirements.txt -r requirements-dev.txt && \
		sha256sum requirements*.txt > $(PY_ENV)/requirements.sha256 ; \
	fi

quiet_cmd_pyenvuninstall = PYENV     uninstall   $2
      cmd_pyenvuninstall = \
	rm -f $(PY_ENV)/requirements.sha256; \
	$(PY_ENV_ACT); \
	python -m pip uninstall --yes -r requirements.txt -r requirements-dev.txt 

# About python packaging see `Python Packaging Authority`_.  Most of the names
# here are mapped to ``setup(<name1>=..., <name2>=...)`` arguments in
# ``setup.py``.  See `Packaging and distributing projects`_ about ``setup(...)``
# arguments. If this is all new for you, start with `PyPI Quick and Dirty`_.
#
# Further read:
#
# - pythonwheels_
# - setuptools_
# - packaging_
# - sdist_
# - installing_
#
# .. _`Python Packaging Authority`: https://www.pypa.io
# .. _`Packaging and distributing projects`: https://packaging.python.org/guides/distributing-packages-using-setuptools/
# .. _`PyPI Quick and Dirty`: https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
# .. _pythonwheels: https://pythonwheels.com/
# .. _setuptools: https://setuptools.readthedocs.io/en/latest/setuptools.html
# .. _packaging: https://packaging.python.org/guides/distributing-packages-using-setuptools/#packaging-and-distributing-projects
# .. _sdist: https://packaging.python.org/guides/distributing-packages-using-setuptools/#source-distributions
# .. _bdist_wheel: https://packaging.python.org/guides/distributing-packages-using-setuptools/#pure-python-wheels
# .. _installing: https://packaging.python.org/tutorials/installing-packages/
#
quiet_cmd_pybuild     = BUILD     $@
      cmd_pybuild     = $(PY_ENV_BIN)/python setup.py \
			sdist -d $(PYDIST)  \
			bdist_wheel --bdist-dir $(PYBUILD) -d $(PYDIST)

# remove 'build' folder since bdist_wheel does not care the --bdist-dir
quiet_cmd_pyclean     = CLEAN     $@
      cmd_pyclean     = \
	rm -rf $(PYDIST) $(PYBUILD) $(PY_ENV) *.egg-info     ;\
	find . -name '*.pyc' -exec rm -f {} +      ;\
	find . -name '*.pyo' -exec rm -f {} +      ;\
	find . -name __pycache__ -exec rm -rf {} +


# to build *local* environment, python from the OS is needed!
PHONY += pyenv
pyenv:
	$(call cmd,pyenv)

# for installation use the pip from PY_ENV (not the OS)!
PHONY += pyenvinstall
pyenvinstall: pyenv
	$(call cmd,pyenvinstall)

# Uninstall the packages.  Since pip does not uninstall the no longer needed
# dependencies (something like autoremove) the depencies remain.
PHONY += pyenvuninstall
pyenvuninstall: pyenv
	$(call cmd,pyenvuninstall)

PHONY += pyclean
pyclean:
	$(call cmd,pyclean)

PHONY += pybuild
pybuild: pyenvinstall
	$(call cmd,pybuild)


# pypi upload
# -----------

# With 'dependency_links=' setuptools supports dependencies on packages hosted
# on other reposetories then PyPi, see "Packages Not On PyPI" [1].  The big
# drawback is, due to security reasons (I don't know where the security gate on
# PyPi is), this feature is not supported by pip [2]. Thats why an upload to
# PyPi is required and since uploads via setuptools is not recommended, we have
# to imstall / use twine ... its really a mess.
#
# [1] https://python-packaging.readthedocs.io/en/latest/dependencies.html#packages-not-on-pypi
# [2] https://github.com/pypa/pip/pull/1519

# https://github.com/pypa/twine
PHONY += upload-pypi upload-pypi-test
upload-pypi: pyclean pyenvinstall pybuild
	@$(PY_ENV_BIN)/twine upload $(PYDIST)/*

upload-pypi-test: pyclean pyenvinstall pybuild
	@$(PY_ENV_BIN)/twine upload -r testpypi $(PYDIST)/*


# update project files
# --------------------

PHONY += project engines.languages useragents.update buildenv

project: buildenv useragents.update engines.languages

engines.languages:  pyenvinstall
	$(Q)echo "fetch languages .."
	$(Q)$(PY_ENV_ACT); python utils/fetch_languages.py
	$(Q)echo "update searx/data/engines_languages.json"
	$(Q)mv engines_languages.json searx/data/engines_languages.json
	$(Q)echo "update searx/languages.py"
	$(Q)mv languages.py searx/languages.py

useragents.update:  pyenvinstall
	$(Q)echo "Update searx/data/useragents.json with the most recent versions of Firefox."
	$(Q)$(PY_ENV_ACT); python utils/fetch_firefox_version.py

buildenv: pyenvinstall
	$(Q)$(PY_ENV_ACT); SEARX_DEBUG=1 python utils/build_env.py

# node / npm
# ----------

node.env: buildenv
	$(Q)./manage.sh npm_packages

node.clean:
	$(Q)echo "CLEAN     locally installed npm dependencies"
	$(Q)rm -rf \
	  ./node_modules  \
	  ./package-lock.json \
	  ./searx/static/themes/oscar/package-lock.json \
	  ./searx/static/themes/oscar/node_modules \
	  ./searx/static/themes/simple/package-lock.json \
	  ./searx/static/themes/simple/node_modules

# build themes
# ------------

PHONY += themes.bootstrap themes themes.oscar themes.simple
themes: buildenv themes.bootstrap themes.oscar themes.simple

quiet_cmd_lessc = LESSC     $3
      cmd_lessc = PATH="$$(npm bin):$$PATH" \
	lessc --clean-css="--s1 --advanced --compatibility=ie9" "searx/static/$2" "searx/static/$3"

quiet_cmd_grunt = GRUNT     $2
      cmd_grunt = PATH="$$(npm bin):$$PATH" \
	grunt --gruntfile  "$2"

themes.oscar: node.env
	$(Q)echo '[!] build oscar theme'
	$(call cmd,grunt,searx/static/themes/oscar/gruntfile.js)

themes.simple: node.env
	$(Q)echo '[!] build simple theme'
	$(call cmd,grunt,searx/static/themes/simple/gruntfile.js)

themes.bootstrap: node.env
	$(call cmd,lessc,less/bootstrap/bootstrap.less,css/bootstrap.min.css)


# docker
# ------

PHONY += docker
docker: buildenv
	$(Q)./manage.sh docker_build

docker.push: buildenv
	$(Q)./manage.sh docker_build push


# gecko
# -----

PHONY += gecko.driver
gecko.driver:
	$(PY_ENV_ACT); ./manage.sh install_geckodriver


# search.checker
# --------------

search.checker: pyenvinstall
	$(Q)$(PY_ENV_ACT); searx-checker -v

ENGINE_TARGETS=$(patsubst searx/engines/%.py,search.checker.%,$(wildcard searx/engines/[!_]*.py))

$(ENGINE_TARGETS): pyenvinstall
	$(Q)$(PY_ENV_ACT); searx-checker -v "$(subst _, ,$(patsubst search.checker.%,%,$@))"


# test
# ----

PHONY += test test.sh test.pep8 test.pylint test.unit test.coverage test.robot
test: buildenv test.pep8 test.pylint test.unit test.robot

PYLINT_FILES=\
	searx/preferences.py \
	searx/testing.py \
	searx/engines/gigablast.py \
	searx/engines/deviantart.py \
	searx/engines/digg.py \
	searx/engines/google.py \
	searx/engines/google_news.py \
	searx/engines/google_videos.py \
	searx/engines/google_images.py

# $2 path to lint
quiet_cmd_pylint      = LINT      $2
      cmd_pylint      = $(PY_ENV_BIN)/python -m pylint -j 0 --rcfile .pylintrc $2

test.pylint: pyenvinstall
	$(call cmd,pylint,$(PYLINT_FILES))
	$(call cmd,pylint,\
		--disable=$(PYLINT_SEARX_DISABLE_OPTION) \
		--additional-builtins=$(PYLINT_ADDITIONAL_BUILTINS_FOR_ENGINES) \
		searx/engines \
	)
	$(call cmd,pylint,\
		--disable=$(PYLINT_SEARX_DISABLE_OPTION) \
		--ignore=searx/engines \
		searx tests \
	)

# ignored rules:
#  E402 module level import not at top of file
#  W503 line break before binary operator

# ubu1604: uses shellcheck v0.3.7 (from 04/2015), no longer supported!
test.sh:
	shellcheck -x -s bash utils/brand.env
	shellcheck -x utils/lib.sh
	shellcheck -x utils/filtron.sh
	shellcheck -x utils/searx.sh
	shellcheck -x utils/morty.sh
	shellcheck -x utils/lxc.sh
	shellcheck -x utils/lxc-searx.env
	shellcheck -x .config.sh

test.pep8: pyenvinstall
	@echo "TEST      pycodestyle (formerly pep8)"
	$(Q)$(PY_ENV_ACT); pycodestyle --exclude='searx/static, searx/languages.py, $(foreach f,$(PYLINT_FILES),$(f),)' \
        --max-line-length=120 --ignore "E117,E252,E402,E722,E741,W503,W504,W605" searx tests

test.unit: pyenvinstall
	@echo "TEST      tests/unit"
	$(Q)$(PY_ENV_ACT); python -m nose2 -s tests/unit

test.coverage:  pyenvinstall
	@echo "TEST      unit test coverage"
	$(Q)$(PY_ENV_ACT); \
	python -m nose2 -C --log-capture --with-coverage --coverage searx -s tests/unit \
	&& coverage report \
	&& coverage html \

test.robot: pyenvinstall gecko.driver
	@echo "TEST      robot"
	$(Q)$(PY_ENV_ACT); PYTHONPATH=. python searx/testing.py robot

test.clean:
	@echo "CLEAN     intermediate test stuff"
	$(Q)rm -rf geckodriver.log .coverage coverage/


# CI
# --

PHONY += ci.test
ci.test:
	$(PY_ENV_BIN)/python -c "import yaml"  || make clean
	$(MAKE) test

.PHONY: $(PHONY)
