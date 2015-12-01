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

robot: .installed.cfg
	@bin/robot

flake8: .installed.cfg
	@bin/flake8 setup.py
	@bin/flake8 ./searx/

tests: .installed.cfg flake8
	@bin/test
	@grunt test --gruntfile searx/static/themes/oscar/gruntfile.js

coverage: .installed.cfg
	@bin/coverage run bin/test
	@bin/coverage report
	@bin/coverage html

production: bin/buildout production.cfg setup.py
	bin/buildout -c production.cfg $(options)
	@echo "* Please modify `readlink --canonicalize-missing ./searx/settings.py`"
	@echo "* Hint 1: on production, disable debug mode and change secret_key"
	@echo "* Hint 2: searx will be executed at server startup by crontab"
	@echo "* Hint 3: to run immediatley, execute 'bin/supervisord'"

minimal: bin/buildout minimal.cfg setup.py
	bin/buildout -c minimal.cfg $(options)

styles:
	@lessc -x searx/static/themes/default/less/style.less > searx/static/themes/default/css/style.css
	@lessc -x searx/static/themes/default/less/style-rtl.less > searx/static/themes/default/css/style-rtl.css
	@lessc -x searx/static/themes/courgette/less/style.less > searx/static/themes/courgette/css/style.css
	@lessc -x searx/static/themes/courgette/less/style-rtl.less > searx/static/themes/courgette/css/style-rtl.css
	@lessc -x searx/static/less/bootstrap/bootstrap.less > searx/static/css/bootstrap.min.css
	@lessc -x searx/static/themes/oscar/less/oscar/oscar.less > searx/static/themes/oscar/css/oscar.min.css
	@lessc -x searx/static/themes/pix-art/less/style.less > searx/static/themes/pix-art/css/style.css

grunt:
	@grunt --gruntfile searx/static/themes/oscar/gruntfile.js

locales:
	@pybabel compile -d searx/translations

clean:
	@rm -rf .installed.cfg .mr.developer.cfg bin parts develop-eggs eggs \
		searx.egg-info lib include .coverage coverage

.PHONY: all tests robot flake8 coverage production minimal styles locales clean
