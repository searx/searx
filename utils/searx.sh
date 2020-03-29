#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh indent-tabs-mode: nil -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# shellcheck disable=SC2001

# shellcheck source=utils/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
# shellcheck source=utils/brand.env
source "${REPO_ROOT}/utils/brand.env"
source_dot_config
source "${REPO_ROOT}/utils/lxc-searx.env"
in_container && lxc_set_suite_env

# ----------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------

PUBLIC_URL="${PUBLIC_URL:-http://$(uname -n)/searx}"

SEARX_INTERNAL_URL="${SEARX_INTERNAL_URL:-127.0.0.1:8888}"

SEARX_URL_PATH="${SEARX_URL_PATH:-$(echo "${PUBLIC_URL}" \
| sed -e 's,^.*://[^/]*\(/.*\),\1,g')}"
[[ "${SEARX_URL_PATH}" == "${PUBLIC_URL}" ]] && SEARX_URL_PATH=/
SEARX_INSTANCE_NAME="${SEARX_INSTANCE_NAME:-searx@$(echo "$PUBLIC_URL" \
| sed -e 's,^.*://\([^\:/]*\).*,\1,g') }"

SERVICE_NAME="searx"
SERVICE_USER="${SERVICE_USER:-${SERVICE_NAME}}"
SERVICE_HOME_BASE="${SERVICE_HOME_BASE:-/usr/local}"
SERVICE_HOME="${SERVICE_HOME_BASE}/${SERVICE_USER}"
# shellcheck disable=SC2034
SERVICE_GROUP="${SERVICE_USER}"

GIT_BRANCH="${GIT_BRANCH:-master}"
SEARX_PYENV="${SERVICE_HOME}/searx-pyenv"
SEARX_SRC="${SERVICE_HOME}/searx-src"
SEARX_SETTINGS_PATH="/etc/searx/settings.yml"
SEARX_UWSGI_APP="searx.ini"
# shellcheck disable=SC2034
SEARX_UWSGI_SOCKET="/run/uwsgi/app/searx/socket"

# apt packages
SEARX_PACKAGES_debian="\
python3-dev python3-babel python3-venv
uwsgi uwsgi-plugin-python3
git build-essential libxslt-dev zlib1g-dev libffi-dev libssl-dev"

BUILD_PACKAGES_debian="\
shellcheck graphviz imagemagick texlive-xetex librsvg2-bin
texlive-latex-recommended texlive-extra-utils ttf-dejavu"

# pacman packages
SEARX_PACKAGES_arch="\
python python-pip python-lxml python-babel
uwsgi uwsgi-plugin-python
git base-devel libxml2"

BUILD_PACKAGES_arch="\
shellcheck graphviz imagemagick texlive-bin extra/librsvg
texlive-core texlive-latexextra ttf-dejavu"

# dnf packages
SEARX_PACKAGES_fedora="\
python python-pip python-lxml python-babel
uwsgi uwsgi-plugin-python3
git @development-tools libxml2"

BUILD_PACKAGES_fedora="\
ShellCheck graphviz graphviz-gd ImageMagick librsvg2-tools
texlive-xetex-bin texlive-collection-fontsrecommended
texlive-collection-latex dejavu-sans-fonts dejavu-serif-fonts
dejavu-sans-mono-fonts"

case $DIST_ID in
    ubuntu|debian)
        SEARX_PACKAGES="${SEARX_PACKAGES_debian}"
        BUILD_PACKAGES="${BUILD_PACKAGES_debian}"
        ;;
    arch)
        SEARX_PACKAGES="${SEARX_PACKAGES_arch}"
        BUILD_PACKAGES="${BUILD_PACKAGES_arch}"
        ;;
    fedora)
        SEARX_PACKAGES="${SEARX_PACKAGES_fedora}"
        BUILD_PACKAGES="${BUILD_PACKAGES_fedora}"
        ;;
esac

# Apache Settings

APACHE_APT_PACKAGES="\
  libapache2-mod-uwsgi \
"

APACHE_SEARX_SITE="searx.conf"

# shellcheck disable=SC2034
CONFIG_FILES=(
    "${uWSGI_APPS_AVAILABLE}/${SEARX_UWSGI_APP}"
)

# shellcheck disable=SC2034
CONFIG_BACKUP_ENCRYPTED=(
    "${SEARX_SETTINGS_PATH}"
)

# ----------------------------------------------------------------------------
usage() {
# ----------------------------------------------------------------------------

    # shellcheck disable=SC1117
    cat <<EOF

usage::

  $(basename "$0") shell
  $(basename "$0") install    [all|user|searx-src|pyenv|uwsgi|apache|packages]
  $(basename "$0") update     [searx]
  $(basename "$0") remove     [all|user|pyenv|searx-src]
  $(basename "$0") activate   [service]
  $(basename "$0") deactivate [service]
  $(basename "$0") inspect    [service]
  $(basename "$0") option     [debug-on|debug-off]
  $(basename "$0") apache     [install|remove]

shell
  start interactive shell from user ${SERVICE_USER}
install / remove
  :all:        complete (de-) installation of searx service
  :user:       add/remove service user '$SERVICE_USER' ($SERVICE_HOME)
  :searx-src:  clone $GIT_URL
  :pyenv:      create/remove virtualenv (python) in $SEARX_PYENV
  :uwsgi:      install searx uWSGI application
  :settings:   reinstall settings from ${REPO_ROOT}/searx/settings.yml
  :packages:   install needed packages from OS package manager
  :buildhost:  install packages from OS package manager needed by buildhost
update searx
  Update searx installation ($SERVICE_HOME)
activate service
  activate and start service daemon (systemd unit)
deactivate service
  stop and deactivate service daemon (systemd unit)
inspect service
  run some small tests and inspect service's status and log
option
  set one of the available options
apache
  :install: apache site with the searx uwsgi app
  :remove:  apache site ${APACHE_FILTRON_SITE}

searx settings: ${SEARX_SETTINGS_PATH}

If needed, set PUBLIC_URL of your WEB service in the '${DOT_CONFIG#"$REPO_ROOT/"}' file::

  PUBLIC_URL          : ${PUBLIC_URL}
  SEARX_INSTANCE_NAME : ${SEARX_INSTANCE_NAME}
  SERVICE_USER        : ${SERVICE_USER}

EOF
    [[ -n ${1} ]] &&  err_msg "$1"
}

main() {
    rst_title "$SEARX_INSTANCE_NAME" part

    required_commands \
        sudo systemctl install git wget curl \
        || exit

    local _usage="unknown or missing $1 command $2"

    case $1 in
        --source-only)  ;;
        -h|--help) usage; exit 0;;

        shell)
            sudo_or_exit
            interactive_shell "${SERVICE_USER}"
            ;;
        inspect)
            case $2 in
                service)
                    sudo_or_exit
                    inspect_service
                    ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        install)
            sudo_or_exit
            case $2 in
                all) install_all ;;
                user) assert_user ;;
                pyenv) create_pyenv ;;
                searx-src) clone_searx ;;
                settings) install_settings ;;
                uwsgi) install_searx_uwsgi;;
                packages)
                    pkg_install "$SEARX_PACKAGES"
                    ;;
                buildhost)
                    pkg_install "$SEARX_PACKAGES"
                    pkg_install "$BUILD_PACKAGES"
                    ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        update)
            sudo_or_exit
            case $2 in
                searx) update_searx;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        remove)
            sudo_or_exit
            case $2 in
                all) remove_all;;
                user) drop_service_account "${SERVICE_USER}";;
                pyenv) remove_pyenv ;;
                searx-src) remove_searx ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        activate)
            sudo_or_exit
            case $2 in
                service)
                    activate_service ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        deactivate)
            sudo_or_exit
            case $2 in
                service)  deactivate_service ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        option)
            sudo_or_exit
            case $2 in
                debug-on)  echo; enable_debug ;;
                debug-off)  echo; disable_debug ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        apache)
            sudo_or_exit
            case $2 in
                install) install_apache_site ;;
                remove) remove_apache_site ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        doc) rst-doc;;

        *) usage "unknown or missing command $1"; exit 42;;
    esac
}

_service_prefix="  ${_Yellow}|$SERVICE_USER|${_creset} "

install_all() {
    rst_title "Install $SEARX_INSTANCE_NAME (service)"
    pkg_install "$SEARX_PACKAGES"
    wait_key
    case $DIST_ID-$DIST_VERS in
        fedora-*)
            systemctl enable uwsgi
            ;;
    esac
    assert_user
    wait_key
    clone_searx
    wait_key
    create_pyenv
    wait_key
    install_settings
    wait_key
    test_local_searx
    wait_key
    install_searx_uwsgi
    if ! service_is_available "http://$SEARX_INTERNAL_URL"; then
        err_msg "URL http://$SEARX_INTERNAL_URL not available, check searx & uwsgi setup!"
    fi
    if ask_yn "Do you want to inspect the installation?" Ny; then
        inspect_service
    fi
}

update_searx() {
    rst_title "Update searx instance"

    echo
    tee_stderr 0.3 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
git checkout -B "$GIT_BRANCH"
git pull
${SEARX_SRC}/manage.sh update_packages
EOF
    install_settings
    uWSGI_restart "$SEARX_UWSGI_APP"
}

remove_all() {
    rst_title "De-Install $SEARX_INSTANCE_NAME (service)"

    rst_para "\
It goes without saying that this script can only be used to remove
installations that were installed with this script."

    if ! ask_yn "Do you really want to deinstall $SEARX_INSTANCE_NAME?"; then
        return
    fi
    remove_searx_uwsgi
    drop_service_account "${SERVICE_USER}"
    remove_settings
    wait_key
    if service_is_available "${PUBLIC_URL}"; then
        MSG="** Don't forgett to remove your public site! (${PUBLIC_URL}) **" wait_key 10
    fi
}

assert_user() {
    rst_title "user $SERVICE_USER" section
    echo
    tee_stderr 1 <<EOF | bash | prefix_stdout
useradd --shell /bin/bash --system \
 --home-dir "$SERVICE_HOME" \
 --comment 'Privacy-respecting metasearch engine' $SERVICE_USER
mkdir "$SERVICE_HOME"
chown -R "$SERVICE_GROUP:$SERVICE_GROUP" "$SERVICE_HOME"
groups $SERVICE_USER
EOF
    #SERVICE_HOME="$(sudo -i -u "$SERVICE_USER" echo \$HOME)"
    #export SERVICE_HOME
    #echo "export SERVICE_HOME=$SERVICE_HOME"
}

clone_is_available() {
    [[ -f "$SEARX_SRC/.git/config" ]]
}

# shellcheck disable=SC2164
clone_searx() {
    rst_title "Clone searx sources" section
    echo
    SERVICE_HOME="$(sudo -i -u "$SERVICE_USER" echo \$HOME 2>/dev/null)"
    if [[ ! "${SERVICE_HOME}" ]]; then
        err_msg "to clone searx sources, user $SERVICE_USER hast to be created first"
        return 42
    fi
    export SERVICE_HOME
    git_clone "$REPO_ROOT" "$SEARX_SRC" \
              "$GIT_BRANCH" "$SERVICE_USER"

    pushd "${SEARX_SRC}" > /dev/null
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 | prefix_stdout "$_service_prefix"
cd "${SEARX_SRC}"
git remote set-url origin ${GIT_URL}
git config user.email "$ADMIN_EMAIL"
git config user.name "$ADMIN_NAME"
git config --list
EOF
    popd > /dev/null
}

install_settings() {
    rst_title "${SEARX_SETTINGS_PATH}" section
    if ! clone_is_available; then
        err_msg "you have to install searx first"
        exit 42
    fi
    mkdir -p "$(dirname ${SEARX_SETTINGS_PATH})"

    if [[ ! -f ${SEARX_SETTINGS_PATH} ]]; then
        info_msg "install settings ${REPO_ROOT}/searx/settings.yml"
        info_msg "  --> ${SEARX_SETTINGS_PATH}"
        cp "${REPO_ROOT}/searx/settings.yml" "${SEARX_SETTINGS_PATH}"
        configure_searx
        return
    fi

    rst_para "Diff between origin's setting file (+) and current (-):"
    echo
    $DIFF_CMD "${SEARX_SETTINGS_PATH}" "${SEARX_SRC}/searx/settings.yml"

    local action
    choose_one action "What should happen to the settings file? " \
           "keep configuration unchanged" \
           "use origin settings" \
           "start interactiv shell"
    case $action in
        "keep configuration unchanged")
            info_msg "leave settings file unchanged"
            ;;
        "use origin settings")
            backup_file "${SEARX_SETTINGS_PATH}"
            info_msg "install origin settings"
            cp "${SEARX_SRC}/searx/settings.yml" "${SEARX_SETTINGS_PATH}"
            ;;
        "start interactiv shell")
            backup_file "${SEARX_SETTINGS_PATH}"
            echo -e "// exit with [${_BCyan}CTRL-D${_creset}]"
            sudo -H -i
            rst_para 'Diff between new setting file (-) and current (+):'
            echo
            $DIFF_CMD "${SEARX_SRC}/searx/settings.yml" "${SEARX_SETTINGS_PATH}"
            wait_key
            ;;
    esac
}

remove_settings() {
    rst_title "remove searx settings" section
    echo
    info_msg "delete ${SEARX_SETTINGS_PATH}"
    rm -f "${SEARX_SETTINGS_PATH}"
}

remove_searx() {
    rst_title "Drop searx sources" section
    if ask_yn "Do you really want to drop searx sources ($SEARX_SRC)?"; then
        rm -rf "$SEARX_SRC"
    else
        rst_para "Leave searx sources unchanged."
    fi
}

pyenv_is_available() {
    [[ -f "${SEARX_PYENV}/bin/activate" ]]
}

create_pyenv() {
    rst_title "Create virtualenv (python)" section
    echo
    if [[ ! -f "${SEARX_SRC}/manage.sh" ]]; then
        err_msg "to create pyenv for searx, searx has to be cloned first"
        return 42
    fi
    info_msg "create pyenv in ${SEARX_PYENV}"
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
rm -rf "${SEARX_PYENV}"
python3 -m venv "${SEARX_PYENV}"
grep -qFs -- 'source ${SEARX_PYENV}/bin/activate' ~/.profile \
  || echo 'source ${SEARX_PYENV}/bin/activate' >> ~/.profile
EOF
    info_msg "inspect python's virtual environment"
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
command -v python && python --version
EOF
    wait_key
    info_msg "install needed python packages"
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
${SEARX_SRC}/manage.sh update_packages
EOF
}

remove_pyenv() {
    rst_title "Remove virtualenv (python)" section
    if ! ask_yn "Do you really want to drop ${SEARX_PYENV} ?"; then
        return
    fi
    info_msg "remove pyenv activation from ~/.profile"
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
grep -v 'source ${SEARX_PYENV}/bin/activate' ~/.profile > ~/.profile.##
mv ~/.profile.## ~/.profile
EOF
    rm -rf "${SEARX_PYENV}"
}

configure_searx() {
    rst_title "Configure searx" section
    rst_para "Setup searx config located at $SEARX_SETTINGS_PATH"
    echo
    tee_stderr 0.1 <<EOF | sudo -H -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
sed -i -e "s/ultrasecretkey/$(openssl rand -hex 16)/g" "$SEARX_SETTINGS_PATH"
sed -i -e "s/{instance_name}/${SEARX_INSTANCE_NAME}/g" "$SEARX_SETTINGS_PATH"
EOF
}

test_local_searx() {
    rst_title "Testing searx instance localy" section
    echo

    if service_is_available "http://$SEARX_INTERNAL_URL" &>/dev/null; then
        err_msg "URL/port http://$SEARX_INTERNAL_URL is already in use, you"
        err_msg "should stop that service before starting local tests!"
        if ! ask_yn "Continue with local tests?"; then
            return
        fi
    fi
    sed -i -e "s/debug : False/debug : True/g" "$SEARX_SETTINGS_PATH"
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
export SEARX_SETTINGS_PATH="${SEARX_SETTINGS_PATH}"
cd ${SEARX_SRC}
timeout 10 python searx/webapp.py &
sleep 3
curl --location --verbose --head --insecure $SEARX_INTERNAL_URL
EOF
    sed -i -e "s/debug : True/debug : False/g" "$SEARX_SETTINGS_PATH"
}

install_searx_uwsgi() {
    rst_title "Install searx's uWSGI app (searx.ini)" section
    echo
    uWSGI_install_app "$SEARX_UWSGI_APP"
}

remove_searx_uwsgi() {
    rst_title "Remove searx's uWSGI app (searx.ini)" section
    echo
    uWSGI_remove_app "$SEARX_UWSGI_APP"
}

activate_service() {
    rst_title "Activate $SEARX_INSTANCE_NAME (service)" section
    echo
    uWSGI_enable_app "$SEARX_UWSGI_APP"
    uWSGI_restart "$SEARX_UWSGI_APP"
}

deactivate_service() {
    rst_title "De-Activate $SEARX_INSTANCE_NAME (service)" section
    echo
    uWSGI_disable_app "$SEARX_UWSGI_APP"
    uWSGI_restart "$SEARX_UWSGI_APP"
}

enable_debug() {
    warn_msg "Do not enable debug in production enviroments!!"
    info_msg "try to enable debug mode ..."
    tee_stderr 0.1 <<EOF | sudo -H -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
sed -i -e "s/debug : False/debug : True/g" "$SEARX_SETTINGS_PATH"
EOF
    uWSGI_restart "$SEARX_UWSGI_APP"
}

disable_debug() {
    info_msg "try to disable debug mode ..."
    tee_stderr 0.1 <<EOF | sudo -H -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
sed -i -e "s/debug : True/debug : False/g" "$SEARX_SETTINGS_PATH"
EOF
    uWSGI_restart "$SEARX_UWSGI_APP"
}

inspect_service() {
    rst_title "service status & log"
    cat <<EOF

sourced ${DOT_CONFIG#"$REPO_ROOT/"} :

  PUBLIC_URL          : ${PUBLIC_URL}
  SEARX_URL_PATH      : ${SEARX_URL_PATH}
  SEARX_INSTANCE_NAME : ${SEARX_INSTANCE_NAME}
  SEARX_INTERNAL_URL  : ${SEARX_INTERNAL_URL}

EOF

    apache_is_installed && info_msg "Apache is installed."

    if service_account_is_available "$SERVICE_USER"; then
        info_msg "Service account $SERVICE_USER exists."
    else
        err_msg "Service account $SERVICE_USER does not exists!"
    fi

    if pyenv_is_available; then
        info_msg "~$SERVICE_USER: python environment is available."
    else
        err_msg "~$SERVICE_USER: python environment is not available!"
    fi

    if clone_is_available; then
        info_msg "~$SERVICE_USER: Searx software is installed."
    else
        err_msg "~$SERVICE_USER: Missing searx software!"
    fi

    if uWSGI_app_enabled "$SEARX_UWSGI_APP"; then
        info_msg "uWSGI app $SEARX_UWSGI_APP is enabled."
    else
        err_msg "uWSGI app $SEARX_UWSGI_APP not enabled!"
    fi

    uWSGI_app_available "$SEARX_UWSGI_APP" \
        || err_msg "uWSGI app $SEARX_UWSGI_APP not available!"

    if in_container; then
        lxc_suite_info
    else
        info_msg "public URL   --> ${PUBLIC_URL}"
        info_msg "internal URL --> http://${SEARX_INTERNAL_URL}"
    fi

    if ! service_is_available "http://${SEARX_INTERNAL_URL}"; then
        err_msg "uWSGI app (service) at http://${SEARX_INTERNAL_URL} is not available!"
        MSG="${_Green}[${_BCyan}CTRL-C${_Green}] to stop or [${_BCyan}KEY${_Green}] to continue"\
           wait_key
    fi

    if ! service_is_available "${PUBLIC_URL}"; then
        warn_msg "Public service at ${PUBLIC_URL} is not available!"
        if ! in_container; then
            warn_msg "Check if public name is correct and routed or use the public IP from above."
        fi
    fi

    local _debug_on
    if ask_yn "Enable searx debug mode?"; then
        enable_debug
        _debug_on=1
    fi
    echo

    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            systemctl --no-pager -l status "${SERVICE_NAME}"
            ;;
        arch-*)
            systemctl --no-pager -l status "uwsgi@${SERVICE_NAME%.*}"
            ;;
        fedora-*)
            systemctl --no-pager -l status uwsgi
            ;;
    esac

    # shellcheck disable=SC2059
    printf "// use ${_BCyan}CTRL-C${_creset} to stop monitoring the log"
    read -r -s -n1 -t 5
    echo

    while true;  do
        trap break 2
        case $DIST_ID-$DIST_VERS in
            ubuntu-*|debian-*) tail -f /var/log/uwsgi/app/searx.log ;;
            arch-*)  journalctl -f -u "uwsgi@${SERVICE_NAME%.*}" ;;
            fedora-*)  journalctl -f -u uwsgi ;;
        esac
    done

    if [[ $_debug_on == 1 ]]; then
        disable_debug
    fi
    return 0
}

install_apache_site() {
    rst_title "Install Apache site $APACHE_SEARX_SITE"

    rst_para "\
This installs the searx uwsgi app as apache site.  If your server ist public to
the internet you should instead use a reverse proxy (filtron) to block
excessively bot queries."

    ! apache_is_installed && err_msg "Apache is not installed."

    if ! ask_yn "Do you really want to install apache site for searx-uwsgi?"; then
        return
    fi

    pkg_install "$APACHE_APT_PACKAGES"
    a2enmod uwsgi

    echo
    apache_install_site --variant=uwsgi "${APACHE_SEARX_SITE}"

    if ! service_is_available "${PUBLIC_URL}"; then
        err_msg "Public service at ${PUBLIC_URL} is not available!"
    fi
}

remove_apache_site() {

    rst_title "Remove Apache site ${APACHE_SEARX_SITE}"

    rst_para "\
This removes apache site ${APACHE_SEARX_SITE}."

    ! apache_is_installed && err_msg "Apache is not installed."

    if ! ask_yn "Do you really want to continue?"; then
        return
    fi

    apache_remove_site "${APACHE_SEARX_SITE}"
}

rst-doc() {
    local debian="${SEARX_PACKAGES_debian}"
    local arch="${SEARX_PACKAGES_arch}"
    local fedora="${SEARX_PACKAGES_fedora}"
    debian="$(echo "${debian}" | sed 's/.*/          & \\/' | sed '$ s/.$//')"
    arch="$(echo "${arch}"     | sed 's/.*/          & \\/' | sed '$ s/.$//')"
    fedora="$(echo "${fedora}" | sed 's/.*/          & \\/' | sed '$ s/.$//')"

    eval "echo \"$(< "${REPO_ROOT}/docs/build-templates/searx.rst")\""

    # I use ubuntu-20.04 here to demonstrate that versions are also suported,
    # normaly debian-* and ubuntu-* are most the same.

    for DIST_NAME in ubuntu-20.04 arch fedora; do
        (
            DIST_ID=${DIST_NAME%-*}
            DIST_VERS=${DIST_NAME#*-}
            [[ $DIST_VERS =~ $DIST_ID ]] && DIST_VERS=
            uWSGI_distro_setup

            echo -e "\n.. START searx uwsgi-description $DIST_NAME"

            case $DIST_ID-$DIST_VERS in
                ubuntu-*|debian-*)  cat <<EOF
# init.d --> /usr/share/doc/uwsgi/README.Debian.gz
# For uWSGI debian uses the LSB init process, this might be changed
# one day, see https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=833067

create     ${uWSGI_APPS_AVAILABLE}/${SEARX_UWSGI_APP}
enable:    sudo -H ln -s ${uWSGI_APPS_AVAILABLE}/${SEARX_UWSGI_APP} ${uWSGI_APPS_ENABLED}/
start:     sudo -H service uwsgi start   ${SEARX_UWSGI_APP%.*}
restart:   sudo -H service uwsgi restart ${SEARX_UWSGI_APP%.*}
stop:      sudo -H service uwsgi stop    ${SEARX_UWSGI_APP%.*}
disable:   sudo -H rm ${uWSGI_APPS_ENABLED}/${SEARX_UWSGI_APP}
EOF
                ;;
                arch-*) cat <<EOF
# systemd --> /usr/lib/systemd/system/uwsgi@.service
# For uWSGI archlinux uses systemd template units, see
# - http://0pointer.de/blog/projects/instances.html
# - https://uwsgi-docs.readthedocs.io/en/latest/Systemd.html#one-service-per-app-in-systemd

create:    ${uWSGI_APPS_ENABLED}/${SEARX_UWSGI_APP}
enable:    sudo -H systemctl enable   uwsgi@${SEARX_UWSGI_APP%.*}
start:     sudo -H systemctl start    uwsgi@${SEARX_UWSGI_APP%.*}
restart:   sudo -H systemctl restart  uwsgi@${SEARX_UWSGI_APP%.*}
stop:      sudo -H systemctl stop     uwsgi@${SEARX_UWSGI_APP%.*}
disable:   sudo -H systemctl disable  uwsgi@${SEARX_UWSGI_APP%.*}
EOF
                ;;
                fedora-*) cat <<EOF
# systemd --> /usr/lib/systemd/system/uwsgi.service
# The unit file starts uWSGI in emperor mode (/etc/uwsgi.ini), see
# - https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html

create:    ${uWSGI_APPS_ENABLED}/${SEARX_UWSGI_APP}
restart:   sudo -H touch ${uWSGI_APPS_ENABLED}/${SEARX_UWSGI_APP}
disable:   sudo -H rm ${uWSGI_APPS_ENABLED}/${SEARX_UWSGI_APP}
EOF
                ;;
            esac
            echo -e ".. END searx uwsgi-description $DIST_NAME"

            echo -e "\n.. START searx uwsgi-appini $DIST_NAME"
            eval "echo \"$(< "${TEMPLATES}/${uWSGI_APPS_AVAILABLE}/${SEARX_UWSGI_APP}")\""
            echo -e "\n.. END searx uwsgi-appini $DIST_NAME"

        )
    done

}

# ----------------------------------------------------------------------------
main "$@"
# ----------------------------------------------------------------------------
