# -*- coding: utf-8; mode: makefile-gmake -*-

export GIT_URL=https://github.com/asciimoo/searx
export SEARX_URL=https://searx.me
export DOCS_URL=https://asciimoo.github.io/searx

PYOBJECTS = searx
DOC       = docs
PY_SETUP_EXTRAS ?= \[test\]

PYDIST=./dist/py
PYBUILD=./build/py

include utils/makefile.include
include utils/makefile.python
include utils/makefile.sphinx

all: clean install

PHONY += help
help:
	@echo  '  test      - run developer tests'
	@echo  '  docs      - build documentation'
	@echo  '  docs-live - autobuild HTML documentation while editing'
	@echo  '  run       - run developer instance'
	@echo  '  install   - developer install (./local)'
	@echo  '  uninstall - uninstall (./local)'
	@echo  '  gh-pages  - build docs & deploy on gh-pages branch'
	@echo  '  clean     - drop builds and environments'
	@echo  '  project   - re-build generic files of the searx project'
	@echo  '  themes    - re-build build the source of the themes'
	@echo  '  docker    - build Docker image'
	@echo  '  node.env  - download & install npm dependencies locally'
	@echo  ''
	@$(MAKE) -s -f utils/makefile.include make-help
	@echo  ''
	@$(MAKE) -s -f utils/makefile.python python-help

PHONY += install
install: pyenvinstall

PHONY += uninstall
uninstall: pyenvuninstall

PHONY += clean
clean: pyclean node.clean
	$(call cmd,common_clean)

PHONY += run
run:  pyenvinstall
	$(Q) ( \
	sed -i -e "s/debug : False/debug : True/g" ./searx/settings.yml ; \
	sleep 2 ; \
	xdg-open http://127.0.0.1:8888/ ; \
	sleep 3 ; \
	sed -i -e "s/debug : True/debug : False/g" ./searx/settings.yml ; \
	) &
	$(PY_ENV)/bin/python ./searx/webapp.py

# docs
# ----

PHONY += docs
docs:  pyenvinstall sphinx-doc
	$(call cmd,sphinx,html,docs,docs)

PHONY += docs-live
docs-live:  pyenvinstall sphinx-live
	$(call cmd,sphinx_autobuild,html,docs,docs)

$(GH_PAGES)::
	@echo "doc available at --> $(DOCS_URL)"

# update project files
# --------------------

PHONY += project engines.languages searx.brand useragents.update

project: useragents.update engines.languages searx.brand

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

searx.brand:
	$(Q)echo "build searx/brand.py"
	$(Q)echo "GIT_URL = '$(GIT_URL)'"  > searx/brand.py
	$(Q)echo "ISSUE_URL = 'https://github.com/asciimoo/searx/issues'" >> searx/brand.py
	$(Q)echo "SEARX_URL = '$(SEARX_URL)'" >> searx/brand.py
	$(Q)echo "DOCS_URL = '$(DOCS_URL)'" >> searx/brand.py
	$(Q)echo "PUBLIC_INSTANCES = 'https://searx.space'" >> searx/brand.py

# node / npm
# ----------

node.env:
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

PHONY += themes themes.oscar themes.simple
themes: themes.oscar themes.simple

themes.oscar:
	$(Q)echo '[!] Grunt build : oscar theme'
	$(Q)PATH="$$(npm bin):$$PATH" grunt --gruntfile  "searx/static/themes/oscar/gruntfile.js"

themes.simple:
	$(Q)echo '[!] Grunt build : simple theme'
	$(Q)PATH="$$(npm bin):$$PATH" grunt --gruntfile  "searx/static/themes/simple/gruntfile.js"

# build styles
# ------------

PHONY += styles style.legacy style.courgette style.pixart style.bootstrap
styles: style.legacy style.courgette style.pixart style.bootstrap

quiet_cmd_lessc = STYLE     $3
      cmd_lessc = PATH="$$(npm bin):$$PATH" \
	lessc --clean-css="--s1 --advanced --compatibility=ie9" "searx/static/$2" "searx/static/$3"

style.legacy:
	$(call cmd,lessc,themes/legacy/less/style-rtl.less,themes/legacy/css/style-rtl.css)
	$(call cmd,lessc,themes/legacy/less/style.less,themes/legacy/css/style.css)

style.courgette:
	$(call cmd,lessc,themes/courgette/less/style.less,themes/courgette/css/style.css)
	$(call cmd,lessc,themes/courgette/less/style-rtl.less,themes/courgette/css/style-rtl.css)

style.pixart:
	$(call cmd,lessc,themes/pix-art/less/style.less,themes/pix-art/css/style.css)

style.bootstrap:
	$(call cmd,lessc,less/bootstrap/bootstrap.less,css/bootstrap.min.css)


# docker
# ------

PHONY += docker
docker:
	$(Q)./manage.sh docker_build


# test
# ----

PHONY += test test.pylint test.pep8 test.unit test.robot

test: test.pylint test.pep8 test.unit test.robot

# TODO: balance linting with pylint
test.pylint: pyenvinstall
	$(call cmd,pylint,searx/preferences.py)
	$(call cmd,pylint,searx/testing.py)

test.pep8: pyenvinstall
	$(PY_ENV_ACT); ./manage.sh pep8_check

test.unit: pyenvinstall
	$(PY_ENV_ACT); ./manage.sh unit_tests

test.robot: pyenvinstall
	$(PY_ENV_ACT); ./manage.sh install_geckodriver
	$(PY_ENV_ACT); ./manage.sh robot_tests

.PHONY: $(PHONY)
