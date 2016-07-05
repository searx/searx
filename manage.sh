#!/bin/sh

BASE_DIR=$(dirname "`readlink -f "$0"`")
PYTHONPATH=$BASE_DIR
SEARX_DIR="$BASE_DIR/searx"
ACTION=$1

update_packages() {
    pip install --upgrade -r "$BASE_DIR/requirements.txt"
}

update_dev_packages() {
    update_packages
    pip install --upgrade -r "$BASE_DIR/requirements-dev.txt"
}

pep8_check() {
    echo '[!] Running pep8 check'
    # ignored rules:
    #  E402 module level import not at top of file
    #  W503 line break before binary operator
    pep8 --max-line-length=120 --ignore "E402,W503" "$SEARX_DIR" "$BASE_DIR/tests"
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

grunt_build() {
	grunt --gruntfile "$SEARX_DIR/static/themes/oscar/gruntfile.js"
}

locales() {
	pybabel compile -d "$SEARX_DIR/translations"
}

help() {
    [ -z "$1" ] || printf "Error: $1\n"
    echo "Searx manage.sh help

Commands
========
    grunt_build          - Build js files
    help                 - This text
    locales              - Compile locales
    pep8_check           - Pep8 validation
    py_test_coverage     - Unit test coverage
    robot_tests          - Run selenium tests
    styles               - Build less files
    tests                - Run all python tests (pep8, unit, robot)
    unit_tests           - Run unit tests
    update_dev_packages  - Check & update development and production dependency changes
    update_packages      - Check & update dependency changes
"
}

[ "$(command -V "$ACTION" | grep ' function$')" = "" ] \
    && help "action not found" \
    || $ACTION
