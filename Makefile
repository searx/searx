# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

version = 2.7
python = bin/python
options =

all: .installed.cfg

.installed.cfg: bin/buildout buildout.cfg setup.py
	bin/buildout $(options)

bin/buildout: $(python) buildout.cfg bootstrap.py
	$(python) bootstrap.py
	@touch $@

$(python):
	virtualenv -p python$(version) --no-site-packages .
	@touch $@

tests: .installed.cfg
	@bin/test

robot: .installed.cfg
	@bin/robot

flake8: .installed.cfg
	@bin/flake8 setup.py
	@bin/flake8 ./searx/

coverage: .installed.cfg
	@bin/coverage run --source=./searx/ --branch bin/test
	@bin/coverage report --show-missing
	@bin/coverage html --directory ./coverage

production: bin/buildout production.cfg setup.py
	bin/buildout -c production.cfg $(options)
	@echo "* Please modify `readlink --canonicalize-missing ./searx/settings.py`"
	@echo "* Hint 1: on production, disable debug mode and change secret_key"
	@echo "* Hint 2: searx will be executed at server startup by crontab"
	@echo "* Hint 3: to run immediatley, execute 'bin/supervisord'"

minimal: bin/buildout minimal.cfg setup.py
	bin/buildout -c minimal.cfg $(options)

clean:
	@rm -rf .installed.cfg .mr.developer.cfg bin parts develop-eggs \
		searx.egg-info lib include .coverage coverage

.PHONY: all tests robot flake8 coverage production minimal clean
