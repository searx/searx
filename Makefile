# -*- coding: utf-8; mode: makefile-gmake -*-
.DEFAULT_GOAL=help

# START Makefile setup
export GIT_URL=https://github.com/searx/searx
export GIT_BRANCH=master
export SEARX_URL=https://searx.me
export DOCS_URL=https://searx.github.io/searx
# END Makefile setup

include utils/makefile.include

PYOBJECTS = searx
DOC       = docs
PY_SETUP_EXTRAS ?= \[test\]
PYLINT_SEARX_DISABLE_OPTION := I,C,R,W0105,W0212,W0511,W0603,W0613,W0621,W0702,W0703,W1401
PYLINT_ADDITIONAL_BUILTINS_FOR_ENGINES := supported_languages,language_aliases

include utils/makefile.python
include utils/makefile.sphinx

all: clean install

PHONY += help-min help-all help

help: help-min
	@echo  ''
	@echo  'to get more help:  make help-all'

help-min:
	@echo  '  test      - run developer tests'
	@echo  '  docs      - build documentation'
	@echo  '  docs-live - autobuild HTML documentation while editing'
	@echo  '  run       - run developer instance'
	@echo  '  install   - developer install (./local)'
	@echo  '  uninstall - uninstall (./local)'
	@echo  '  gh-pages  - build docs & deploy on gh-pages branch'
	@echo  '  clean     - drop builds and environments'
	@echo  '  project   - re-build generic files of the searx project'
	@echo  '  buildenv  - re-build environment files (aka brand)'
	@echo  '  themes    - re-build build the source of the themes'
	@echo  '  docker    - build Docker image'
	@echo  '  node.env  - download & install npm dependencies locally'
	@echo  ''
	@echo  'environment'
	@echo  '  SEARX_URL = $(SEARX_URL)'
	@echo  '  GIT_URL   = $(GIT_URL)'
	@echo  '  DOCS_URL  = $(DOCS_URL)'
	@echo  ''
	@$(MAKE) -e -s make-help

help-all: help-min
	@echo  ''
	@$(MAKE) -e -s python-help
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

PHONY += prebuild-includes
prebuild-includes:
	$(Q)mkdir -p $(DOCS_BUILD)/includes
	$(Q)./utils/searx.sh doc | cat > $(DOCS_BUILD)/includes/searx.rst
	$(Q)./utils/filtron.sh doc | cat > $(DOCS_BUILD)/includes/filtron.rst
	$(Q)./utils/morty.sh doc | cat > $(DOCS_BUILD)/includes/morty.rst


$(GH_PAGES)::
	@echo "doc available at --> $(DOCS_URL)"

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

buildenv:
	$(Q)echo "build searx/brand.py"
	$(Q)echo "GIT_URL = '$(GIT_URL)'"  > searx/brand.py
	$(Q)echo "GIT_BRANCH = '$(GIT_BRANCH)'"  >> searx/brand.py
	$(Q)echo "ISSUE_URL = 'https://github.com/searx/searx/issues'" >> searx/brand.py
	$(Q)echo "SEARX_URL = '$(SEARX_URL)'" >> searx/brand.py
	$(Q)echo "DOCS_URL = '$(DOCS_URL)'" >> searx/brand.py
	$(Q)echo "PUBLIC_INSTANCES = 'https://searx.space'" >> searx/brand.py
	$(Q)echo "build utils/brand.env"
	$(Q)echo "export GIT_URL='$(GIT_URL)'"  > utils/brand.env
	$(Q)echo "export GIT_BRANCH='$(GIT_BRANCH)'"  >> utils/brand.env
	$(Q)echo "export ISSUE_URL='https://github.com/searx/searx/issues'" >> utils/brand.env
	$(Q)echo "export SEARX_URL='$(SEARX_URL)'" >> utils/brand.env
	$(Q)echo "export DOCS_URL='$(DOCS_URL)'" >> utils/brand.env
	$(Q)echo "export PUBLIC_INSTANCES='https://searx.space'" >> utils/brand.env


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

PHONY += themes.bootstrap themes themes.oscar themes.simple themes.legacy themes.courgette themes.pixart
themes: buildenv themes.bootstrap themes.oscar themes.simple themes.legacy themes.courgette themes.pixart

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

themes.legacy: node.env
	$(Q)echo '[!] build legacy theme'
	$(call cmd,lessc,themes/legacy/less/style-rtl.less,themes/legacy/css/style-rtl.css)
	$(call cmd,lessc,themes/legacy/less/style.less,themes/legacy/css/style.css)

themes.courgette: node.env
	$(Q)echo '[!] build courgette theme'
	$(call cmd,lessc,themes/courgette/less/style.less,themes/courgette/css/style.css)
	$(call cmd,lessc,themes/courgette/less/style-rtl.less,themes/courgette/css/style-rtl.css)

themes.pixart: node.env
	$(Q)echo '[!] build pixart theme'
	$(call cmd,lessc,themes/pix-art/less/style.less,themes/pix-art/css/style.css)

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

# test
# ----

PHONY += test test.sh test.pylint test.pep8 test.unit test.coverage test.robot
test: buildenv test.pylint test.pep8 test.unit gecko.driver test.robot

PYLINT_FILES=\
	searx/preferences.py \
	searx/testing.py \
	searx/engines/gigablast.py \
	searx/engines/deviantart.py \
	searx/engines/digg.py

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


# travis
# ------

travis.codecov:
	$(Q)$(PY_ENV_BIN)/python -m pip install codecov

.PHONY: $(PHONY)
