#!/bin/sh

BASE_DIR=$(dirname "`readlink -f "$0"`")
PYTHONPATH=$BASE_DIR
SEARX_DIR="$BASE_DIR/searx"
ACTION=$1

cd "$BASE_DIR"

update_packages() {
    pip install --upgrade pip
    pip install --upgrade setuptools
    pip install -r "$BASE_DIR/requirements.txt"
}

update_dev_packages() {
    update_packages
    pip install -r "$BASE_DIR/requirements-dev.txt"
}

install_geckodriver() {
    echo '[!] Checking geckodriver'
    # TODO : check the current geckodriver version
    set -e
    geckodriver -V 2>1 > /dev/null || NOTFOUND=1
    set +e
    if [ -z $NOTFOUND ]; then
	return
    fi
    GECKODRIVER_VERSION="v0.18.0"
    PLATFORM=`python -c "import six; import platform; six.print_(platform.system().lower(), platform.architecture()[0])"`
    case $PLATFORM in
	"linux 32bit" | "linux2 32bit") ARCH="linux32";;
	"linux 64bit" | "linux2 64bit") ARCH="linux64";;
	"windows 32 bit") ARCH="win32";;
	"windows 64 bit") ARCH="win64";;
	"mac 64bit") ARCH="macos";;
    esac
    GECKODRIVER_URL="https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-$ARCH.tar.gz";

    if [ -z "$1" ]; then
	if [ -z "$VIRTUAL_ENV" ]; then
	    echo "geckodriver can't be installed because VIRTUAL_ENV is not set, you should download it from\n  $GECKODRIVER_URL"
	    exit    
	else
	    GECKODRIVER_DIR="$VIRTUAL_ENV/bin"
	fi
    else
	GECKODRIVER_DIR="$1"
	mkdir -p "$GECKODRIVER_DIR"
    fi

    echo "Installing $GECKODRIVER_DIR/geckodriver from\n  $GECKODRIVER_URL"
    
    FILE=`mktemp`
    wget "$GECKODRIVER_URL" -qO $FILE && tar xz -C "$GECKODRIVER_DIR" -f $FILE geckodriver
    rm $FILE
    chmod 777 "$GECKODRIVER_DIR/geckodriver"
}

pep8_check() {
    echo '[!] Running pep8 check'
    # ignored rules:
    #  E402 module level import not at top of file
    #  W503 line break before binary operator
    pep8 --exclude=searx/static --max-line-length=120 --ignore "E402,W503" "$SEARX_DIR" "$BASE_DIR/tests"
}

unit_tests() {
    echo '[!] Running unit tests'
    python -m nose2 -s "$BASE_DIR/tests/unit"
}

py_test_coverage() {
    echo '[!] Running python test coverage'
    PYTHONPATH=`pwd` python -m nose2 -C --log-capture --with-coverage --coverage "$SEARX_DIR" -s "$BASE_DIR/tests/unit" \
    && coverage report \
    && coverage html
}

robot_tests() {
    echo '[!] Running robot tests'
    PYTHONPATH=`pwd` python "$SEARX_DIR/testing.py" robot
}

tests() {
    set -e
    pep8_check
    unit_tests
    install_geckodriver
    robot_tests
    set +e
}

build_style() {
    lessc --clean-css="--s1 --advanced --compatibility=ie9" "$BASE_DIR/searx/static/$1" "$BASE_DIR/searx/static/$2"
}

styles() {
    echo '[!] Building styles'
    build_style themes/legacy/less/style.less themes/legacy/css/style.css
    build_style themes/legacy/less/style-rtl.less themes/legacy/css/style-rtl.css
    build_style themes/courgette/less/style.less themes/courgette/css/style.css
    build_style themes/courgette/less/style-rtl.less themes/courgette/css/style-rtl.css
    build_style less/bootstrap/bootstrap.less css/bootstrap.min.css
    build_style themes/pix-art/less/style.less themes/pix-art/css/style.css
    # built using grunt
    #build_style themes/oscar/less/pointhi/oscar.less themes/oscar/css/pointhi.min.css
    #build_style themes/oscar/less/logicodev/oscar.less themes/oscar/css/logicodev.min.css
    #build_style themes/simple/less/style.less themes/simple/css/searx.min.css
    #build_style themes/simple/less/style-rtl.less themes/simple/css/searx-rtl.min.css
}

npm_packages() {
    echo '[!] install NPM packages for oscar theme'
    cd $BASE_DIR/searx/static/themes/oscar
    npm install

    echo '[!] install NPM packages for simple theme'    
    cd $BASE_DIR/searx/static/themes/simple
    npm install
}

grunt_build() {
    echo '[!] Grunt build : oscar theme'
    grunt --gruntfile "$SEARX_DIR/static/themes/oscar/gruntfile.js"
    echo '[!] Grunt build : simple theme'    
    grunt --gruntfile "$SEARX_DIR/static/themes/simple/gruntfile.js"
}

locales() {
    pybabel compile -d "$SEARX_DIR/translations"
}

help() {
    [ -z "$1" ] || printf "Error: $1\n"
    echo "Searx manage.sh help

Commands
========
    npm_packages         - Download & install dependencies
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
    install_geckodriver  - Download & install geckodriver if not already installed (required for robot_tests)
"
}

[ "$(command -V "$ACTION" | grep ' function$')" = "" ] \
    && help "action not found" \
    || $ACTION "$2"
