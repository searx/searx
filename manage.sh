#!/bin/sh

export LANG=C

BASE_DIR="$(dirname -- "`readlink -f -- "$0"`")"

cd -- "$BASE_DIR"
set -e

# subshell
PYTHONPATH="$BASE_DIR"
SEARX_DIR="$BASE_DIR/searx"
ACTION="$1"

. "${BASE_DIR}/utils/brand.env"

#
# Python
#

update_packages() {
    pip install --upgrade pip
    pip install --upgrade setuptools
    pip install -Ur "$BASE_DIR/requirements.txt"
}

update_dev_packages() {
    update_packages
    pip install -Ur "$BASE_DIR/requirements-dev.txt"
}

install_geckodriver() {
    echo '[!] Checking geckodriver'
    # TODO : check the current geckodriver version
    set -e
    geckodriver -V > /dev/null 2>&1 || NOTFOUND=1
    set +e
    if [ -z "$NOTFOUND" ]; then
        return
    fi
    GECKODRIVER_VERSION="v0.24.0"
    PLATFORM="`python3 -c "import platform; print(platform.system().lower(), platform.architecture()[0])"`"
    case "$PLATFORM" in
        "linux 32bit" | "linux2 32bit") ARCH="linux32";;
        "linux 64bit" | "linux2 64bit") ARCH="linux64";;
        "windows 32 bit") ARCH="win32";;
        "windows 64 bit") ARCH="win64";;
        "mac 64bit") ARCH="macos";;
    esac
    GECKODRIVER_URL="https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-$ARCH.tar.gz";

    if [ -z "$1" ]; then
        if [ -z "$VIRTUAL_ENV" ]; then
            printf "geckodriver can't be installed because VIRTUAL_ENV is not set, you should download it from\n  %s" "$GECKODRIVER_URL"
            exit
        else
            GECKODRIVER_DIR="$VIRTUAL_ENV/bin"
        fi
    else
        GECKODRIVER_DIR="$1"
        mkdir -p -- "$GECKODRIVER_DIR"
    fi

    printf "Installing %s/geckodriver from\n  %s" "$GECKODRIVER_DIR" "$GECKODRIVER_URL"

    FILE="`mktemp`"
    wget -qO "$FILE" -- "$GECKODRIVER_URL" && tar xz -C "$GECKODRIVER_DIR" -f "$FILE" geckodriver
    rm -- "$FILE"
    chmod 777 -- "$GECKODRIVER_DIR/geckodriver"
}

locales() {
    pybabel compile -d "$SEARX_DIR/translations"
}


#
# Web
#

npm_path_setup() {
    which npm || (printf 'Error: npm is not found\n'; exit 1)
    export PATH="$(npm bin)":$PATH
}

npm_packages() {
    npm_path_setup

    echo '[!] install NPM packages'
    cd -- "$BASE_DIR"
    npm install less@2.7 less-plugin-clean-css grunt-cli

    echo '[!] install NPM packages for oscar theme'
    cd -- "$BASE_DIR/searx/static/themes/oscar"
    npm install

    echo '[!] install NPM packages for simple theme'
    cd -- "$BASE_DIR/searx/static/themes/simple"
    npm install
}

docker_build() {
    # Check if it is a git repository
    if [ ! -d .git ]; then
	echo "This is not Git repository"
	exit 1
    fi

    if [ ! -x "$(which git)" ]; then
	echo "git is not installed"
	exit 1
    fi

    if [ ! git remote get-url origin 2> /dev/null ]; then
	echo "there is no remote origin"
	exit 1
    fi

    # This is a git repository

    # "git describe" to get the Docker version (for example : v0.15.0-89-g0585788e)
    # awk to remove the "v" and the "g"
    SEARX_GIT_VERSION=$(git describe --match "v[0-9]*\.[0-9]*\.[0-9]*" HEAD 2>/dev/null | awk -F'-' '{OFS="-"; $1=substr($1, 2); if ($3) { $3=substr($3, 2); }  print}')

    # add the suffix "-dirty" if the repository has uncommited change
    # /!\ HACK for searx/searx: ignore searx/brand.py and utils/brand.env
    git update-index -q --refresh
    if [ ! -z "$(git diff-index --name-only HEAD -- | grep -v 'searx/brand.py' | grep -v 'utils/brand.env')" ]; then
	SEARX_GIT_VERSION="${SEARX_GIT_VERSION}-dirty"
    fi

    # Get the last git commit id, will be added to the Searx version (see Dockerfile)
    VERSION_GITCOMMIT=$(echo $SEARX_GIT_VERSION | cut -d- -f2-4)
    echo "Last commit : $VERSION_GITCOMMIT"

    # Check consistency between the git tag and the searx/version.py file
    # /!\ HACK : parse Python file with bash /!\
    # otherwise it is not possible build the docker image without all Python dependencies ( version.py loads __init__.py )
    # SEARX_PYTHON_VERSION=$(python3 -c "import six; import searx.version; six.print_(searx.version.VERSION_STRING)")
    SEARX_PYTHON_VERSION=$(cat searx/version.py | grep "\(VERSION_MAJOR\|VERSION_MINOR\|VERSION_BUILD\) =" | cut -d\= -f2 | sed -e 's/^[[:space:]]*//' | paste -sd "." -)
    if [ $(echo "$SEARX_GIT_VERSION" | cut -d- -f1) != "$SEARX_PYTHON_VERSION" ]; then
	echo "Inconsistency between the last git tag and the searx/version.py file"
	echo "git tag:          $SEARX_GIT_VERSION"
	echo "searx/version.py: $SEARX_PYTHON_VERSION"
	exit 1
    fi

    # define the docker image name
    GITHUB_USER=$(echo "${GIT_URL}" | sed 's/.*github\.com\/\([^\/]*\).*/\1/')
    SEARX_IMAGE_NAME="${GITHUB_USER:-searx}/searx"

    # build Docker image
    echo "Building image ${SEARX_IMAGE_NAME}:${SEARX_GIT_VERSION}"
    sudo docker build \
         --build-arg GIT_URL="${GIT_URL}" \
         --build-arg SEARX_GIT_VERSION="${SEARX_GIT_VERSION}" \
         --build-arg VERSION_GITCOMMIT="${VERSION_GITCOMMIT}" \
         --build-arg LABEL_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
         --build-arg LABEL_VCS_REF=$(git rev-parse HEAD) \
         --build-arg LABEL_VCS_URL="${GIT_URL}" \
	 --build-arg TIMESTAMP_SETTINGS=$(git log -1 --format="%cd" --date=unix -- searx/settings.yml) \
	 --build-arg TIMESTAMP_UWSGI=$(git log -1 --format="%cd" --date=unix -- dockerfiles/uwsgi.ini) \
         -t ${SEARX_IMAGE_NAME}:latest -t ${SEARX_IMAGE_NAME}:${SEARX_GIT_VERSION} .

    if [ "$1" = "push" ]; then
	sudo docker push ${SEARX_IMAGE_NAME}:latest
	sudo docker push ${SEARX_IMAGE_NAME}:${SEARX_GIT_VERSION}
    fi
}

#
# Help
#

help() {
    [ -z "$1" ] || printf 'Error: %s\n' "$1"
    echo "Searx manage.sh help

Commands
========
    help                 - This text

    Build requirements
    ------------------
    update_packages      - Check & update production dependency changes
    update_dev_packages  - Check & update development and production dependency changes
    install_geckodriver  - Download & install geckodriver if not already installed (required for robot_tests)
    npm_packages         - Download & install npm dependencies

    Build
    -----
    locales              - Compile locales

Environment:
    GIT_URL:          ${GIT_URL}
    ISSUE_URL:        ${ISSUE_URL}
    SEARX_URL:        ${SEARX_URL}
    DOCS_URL:         ${DOCS_URL}
    PUBLIC_INSTANCES: ${PUBLIC_INSTANCES}
"
}

[ "$(command -V "$ACTION" | grep ' function$')" = "" ] \
    && help "action not found" \
    || "$ACTION" "$2"
