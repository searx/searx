# -*- coding: utf-8; mode: makefile-gmake -*-
.DEFAULT_GOAL=help

include utils/makefile.include

PYOBJECTS = searx
DOC       = docs
PY_SETUP_EXTRAS ?= \[test\]
PYLINT_SEARX_DISABLE_OPTION := I,C,R,W0105,W0212,W0511,W0603,W0613,W0621,W0702,W0703,W1401,E1136
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
	$(Q)$(PY_ENV_ACT); python ./searx_extra/update/update_languages.py
	$(Q)echo "updated searx/data/engines_languages.json"
	$(Q)echo "updated searx/languages.py"

useragents.update:  pyenvinstall
	$(Q)echo "fetch useragents .."
	$(Q)$(PY_ENV_ACT); python ./searx_extra/update/update_firefox_version.py
	$(Q)echo "updated searx/data/useragents.json with the most recent versions of Firefox."

buildenv: pyenv
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

PHONY += themes themes.oscar themes.simple
themes: buildenv themes.oscar themes.simple

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

PHONY += test test.sh test.pylint test.pep8 test.unit test.coverage test.robot
test: buildenv test.pylint test.pep8 test.unit gecko.driver test.robot

PYLINT_FILES=\
	searx/preferences.py \
	searx/testing.py \
	searx/engines/gigablast.py \
	searx/engines/deviantart.py \
	searx/engines/digg.py \
	searx/engines/google.py \
	searx/engines/google_news.py \
	searx/engines/google_videos.py \
	searx/engines/google_images.py \
	searx/engines/mediathekviewweb.py \
	searx/engines/meilisearch.py \
	searx/engines/solidtorrents.py \
	searx/engines/solr.py \
	searx/engines/springer.py \
	searx/engines/google_scholar.py \
	searx/engines/yahoo_news.py \
	searx/engines/apkmirror.py \
	searx/engines/artic.py \
	searx_extra/update/update_external_bangs.py \
	searx/metrics/__init__.py

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

PHONY += ci.test
ci.test:
	$(PY_ENV_BIN)/python -c "import yaml"  || make clean
	$(MAKE) test

travis.codecov:
	$(Q)$(PY_ENV_BIN)/python -m pip install codecov

.PHONY: $(PHONY)
