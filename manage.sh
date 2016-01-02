#!/bin/sh

BASE_DIR=$(dirname `readlink -f $0`)
PYTHONPATH=$BASE_DIR
SEARX_DIR="$BASE_DIR/searx"
ACTION=$1

update_packages() {
    pip install --upgrade -r "$BASE_DIR/requirements.txt"
}

update_dev_packages() {
    pip install --upgrade -r "$BASE_DIR/requirements-dev.txt"
}

pep8_check() {
    echo '[!] Running pep8 check'
    pep8 --max-line-length=120 "$SEARX_DIR" "$BASE_DIR/tests"
}

unit_tests() {
    echo '[!] Running unit tests'
    python -m nose2 -s "$BASE_DIR/tests/unit"
}

py_test_coverage() {
    echo '[!] Running python test coverage'
    PYTHONPATH=`pwd` python -m nose2 -C --coverage "$SEARX_DIR" -s "$BASE_DIR/tests/unit"
    coverage report
    coverage html
}

robot_tests() {
    echo '[!] Running robot tests'
    PYTHONPATH=`pwd` python "$SEARX_DIR/testing.py" robot
}

tests() {
    set -e
    pep8_check
    unit_tests
    robot_tests
    set +e
}

build_style() {
    lessc -x "$BASE_DIR/searx/static/$1" "$BASE_DIR/searx/static/$2"
}

styles() {
    echo '[!] Building styles'
	build_style themes/default/less/style.less themes/default/css/style.css
	build_style themes/default/less/style-rtl.less themes/default/css/style-rtl.css
	build_style themes/courgette/less/style.less themes/courgette/css/style.css
	build_style themes/courgette/less/style-rtl.less themes/courgette/css/style-rtl.css
	build_style less/bootstrap/bootstrap.less css/bootstrap.min.css
	build_style themes/oscar/less/oscar/oscar.less themes/oscar/css/oscar.min.css
	build_style themes/pix-art/less/style.less themes/pix-art/css/style.css
}

grunt() {
	grunt --gruntfile "$SEARX_DIR/static/themes/oscar/gruntfile.js"
}

locales() {
	pybabel compile -d "$SEARX_DIR/translations"
}

$ACTION
