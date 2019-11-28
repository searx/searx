# -*- coding: utf-8; mode: makefile-gmake -*-

PYOBJECTS = searx
PY_SETUP_EXTRAS ?= \[test\]

include utils/makefile.include
include utils/makefile.python

all: clean install

PHONY += help
help:
	@echo  '  test      - run developer tests'
	@echo  '  run       - run developer instance'
	@echo  '  install   - developer install (./local)'
	@echo  '  uninstall - uninstall (./local)'
	@echo  ''
	@$(MAKE) -s -f utils/makefile.include make-help
	@echo  ''
	@$(MAKE) -s -f utils/makefile.python python-help

PHONY += install
install: pyenvinstall

PHONY += uninstall
uninstall: pyenvuninstall

PHONY += clean
clean: pyclean
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

# test
# ----

PHONY += test test.pep8 test.unit test.robot

test: test.pep8 test.unit test.robot

test.pep8: pyenvinstall
	$(PY_ENV_ACT); ./manage.sh pep8_check

test.unit: pyenvinstall
	$(PY_ENV_ACT); ./manage.sh unit_tests

test.robot: pyenvinstall
	$(PY_ENV_ACT); ./manage.sh install_geckodriver
	$(PY_ENV_ACT); ./manage.sh robot_tests

.PHONY: $(PHONY)
