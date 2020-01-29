#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh indent-tabs-mode: nil -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# shellcheck disable=SC2001

# shellcheck source=utils/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
source_dot_config

# ----------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------

SEARX_URL_PATH="${SEARX_URL_PATH:-$(echo "${PUBLIC_URL}" \
| sed -e 's,^.*://[^/]*\(/.*\),\1,g')}"
[[ "${SEARX_URL_PATH}" == "${PUBLIC_URL}" ]] && SEARX_URL_PATH=/
SEARX_INSTANCE_NAME="${SEARX_INSTANCE_NAME:-searx@$(echo "$PUBLIC_URL" \
| sed -e 's,^.*://\([^\:/]*\).*,\1,g') }"

SERVICE_USER="searx"
# shellcheck disable=SC2034
SERVICE_GROUP="${SERVICE_USER}"
SERVICE_HOME="/home/${SERVICE_USER}"

SEARX_INTERNAL_URL="127.0.0.1:8888"
SEARX_GIT_URL="https://github.com/asciimoo/searx.git"
SEARX_GIT_BRANCH="master"
SEARX_PYENV="${SERVICE_HOME}/searx-pyenv"
SEARX_SRC="${SERVICE_HOME}/searx-src"
SEARX_SETTINGS="${SEARX_SRC}/searx/settings.yml"
SEARX_UWSGI_APP="searx.ini"
# shellcheck disable=SC2034
SEARX_UWSGI_SOCKET="/run/uwsgi/app/searx/socket"

# FIXME: Arch Linux & RHEL should be added

SEARX_APT_PACKAGES="\
  uwsgi uwsgi-plugin-python3 \
  git build-essential libxslt-dev python3-dev python3-babel zlib1g-dev \
  libffi-dev libssl-dev \
"

# Apache Settings

APACHE_APT_PACKAGES="\
  libapache2-mod-uwsgi \
"

APACHE_SEARX_SITE="searx.conf"

# shellcheck disable=SC2034
CONFIG_FILES=(
    "${uWSGI_SETUP}/apps-available/${SEARX_UWSGI_APP}"
)

# shellcheck disable=SC2034
CONFIG_BACKUP_ENCRYPTED=(
    "${SEARX_SETTINGS}"
)

# ----------------------------------------------------------------------------
usage() {
# ----------------------------------------------------------------------------

    # shellcheck disable=SC1117
    cat <<EOF

usage:

  $(basename "$0") shell
  $(basename "$0") install    [all|user|pyenv|searx-src|apache]
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
  all:        complete (de-) installation of searx service
  user:       add/remove service user '$SERVICE_USER' at $SERVICE_HOME
  searx-src:  clone $SEARX_GIT_URL
  pyenv:      create/remove virtualenv (python) in $SEARX_PYENV
update searx
  Update searx installation of user ${SERVICE_USER}
activate service
  activate and start service daemon (systemd unit)
deactivate service
  stop and deactivate service daemon (systemd unit)
inspect service
  run some small tests and inspect service's status and log
option
  set one of the available options
apache
  install: apache site with the searx uwsgi app
  remove:  apache site ${APACHE_FILTRON_SITE}

If needed change the environment variable PUBLIC_URL of your WEB service in the
${DOT_CONFIG#"$REPO_ROOT/"} file:

  PUBLIC_URL          : ${PUBLIC_URL}
  SEARX_INSTANCE_NAME : ${SEARX_INSTANCE_NAME}

EOF
    [ ! -z ${1+x} ] &&  echo -e "$1"
}

main() {
    rst_title "$SEARX_INSTANCE_NAME" part

    required_commands \
        dpkg systemctl apt-get install git wget curl \
        || exit

    local _usage="ERROR: unknown or missing $1 command $2"

    case $1 in
        --source-only)  ;;
        -h|--help) usage; exit 0;;

        shell)
            sudo_or_exit
            interactive_shell
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
                user) remove_user ;;
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

        *) usage "ERROR: unknown or missing command $1"; exit 42;;
    esac
}

_service_prefix="  |$SERVICE_USER| "

install_all() {
    rst_title "Install $SEARX_INSTANCE_NAME (service)"
    pkg_install "$SEARX_APT_PACKAGES"
    wait_key
    assert_user
    wait_key
    clone_searx
    wait_key
    create_pyenv
    wait_key
    configure_searx
    wait_key
    test_local_searx
    wait_key
    install_searx_uwsgi
    if ! service_is_available "http://$SEARX_INTERNAL_URL"; then
        err_msg "URL http://$SEARX_INTERNAL_URL not available, check searx & uwsgi setup!"
    fi
    if ask_yn "Do you want to inspect the installation?" Yn; then
        inspect_service
    fi

}

update_searx() {
    rst_title "Update searx instance"

    echo
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
cp -f ${SEARX_SETTINGS} ${SEARX_SETTINGS}.backup
git stash push -m "BACKUP -- 'update server' at ($(date))"
git checkout -b $SEARX_GIT_BRANCH" --track "$SEARX_GIT_BRANCH"
git pull "$SEARX_GIT_BRANCH"
${SEARX_SRC}/manage.sh update_packages
EOF
    configure_searx

    rst_title "${SEARX_SETTINGS}" section
    rstBlock 'Diff between new setting file (<) and backup (>):'
    echo
    diff "$SEARX_SETTINGS}" "${SEARX_SETTINGS}.backup"

    local action
    choose_one action "What should happen to the settings file? " \
           "keep new configuration" \
           "revert to the old configuration (backup file)" \
           "start interactiv shell"
    case $action in
        "keep new configuration")
            info_msg "continue using new settings file"
            ;;
        "revert to the old configuration (backup file)")
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
cp -f ${SEARX_SETTINGS}.backup ${SEARX_SETTINGS}
EOF
            ;;
        "start interactiv shell")
            interactive_shell
            ;;
    esac
    chown "${SERVICE_USER}:${SERVICE_USER}" "${SEARX_SETTINGS}"

    # shellcheck disable=SC2016
    rst_para 'Diff between local modified settings (<) and $SEARX_GIT_BRANCH branch (>):'
    echo
    git_diff
    wait_key
    uWSGI_restart
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
    wait_key
    remove_user
}

user_is_available() {
    sudo -i -u "$SERVICE_USER" echo \$HOME &>/dev/null
}

assert_user() {
    rst_title "user $SERVICE_USER" section
    echo
    tee_stderr 1 <<EOF | bash | prefix_stdout
sudo -H adduser --shell /bin/bash --system --home "$SERVICE_HOME" \
  --disabled-password --group --gecos 'searx' $SERVICE_USER
sudo -H usermod -a -G shadow $SERVICE_USER
groups $SERVICE_USER
EOF
    #SERVICE_HOME="$(sudo -i -u "$SERVICE_USER" echo \$HOME)"
    #export SERVICE_HOME
    #echo "export SERVICE_HOME=$SERVICE_HOME"
}

remove_user() {
    rst_title "Drop $SERVICE_USER HOME" section
    if ask_yn "Do you really want to drop $SERVICE_USER home folder?"; then
        userdel -r -f "$SERVICE_USER" 2>&1 | prefix_stdout
    else
        rst_para "Leave HOME folder $(du -sh "$SERVICE_HOME") unchanged."
    fi
}

clone_is_available() {
    [[ -f "$SEARX_SETTINGS" ]]
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

    git_clone "$SEARX_GIT_URL" "$SEARX_SRC" \
              "$SEARX_GIT_BRANCH" "$SERVICE_USER"

    pushd "${SEARX_SRC}" > /dev/null
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 | prefix_stdout "$_service_prefix"
cd "${SEARX_SRC}"
git config user.email "$ADMIN_EMAIL"
git config user.name "$ADMIN_NAME"
git config --list
EOF
    popd > /dev/null
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
    rst_para "Setup searx config located at $SEARX_SETTINGS"
    echo
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
sed -i -e "s/ultrasecretkey/$(openssl rand -hex 16)/g" "$SEARX_SETTINGS"
sed -i -e "s/{instance_name}/${SEARX_INSTANCE_NAME}/g" "$SEARX_SETTINGS"
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
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
sed -i -e "s/debug : False/debug : True/g" "$SEARX_SETTINGS"
timeout 5 python3 searx/webapp.py &
sleep 1
curl --location --verbose --head --insecure $SEARX_INTERNAL_URL
sed -i -e "s/debug : True/debug : False/g" "$SEARX_SETTINGS"
EOF
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
    uWSGI_restart
}

deactivate_service() {
    rst_title "De-Activate $SEARX_INSTANCE_NAME (service)" section
    echo
    uWSGI_disable_app "$SEARX_UWSGI_APP"
    uWSGI_restart
}

interactive_shell() {
    echo "// exit with CTRL-D"
    sudo -H -u "${SERVICE_USER}" -i
}

git_diff() {
    sudo -H -u "${SERVICE_USER}" -i <<EOF
cd ${SEARX_REPO_FOLDER}
git --no-pager diff
EOF
}

enable_debug() {
    info_msg "try to enable debug mode ..."
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
sed -i -e "s/debug : False/debug : True/g" "$SEARX_SETTINGS"
EOF
    uWSGI_restart
}

disable_debug() {
    info_msg "try to disable debug mode ..."
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
sed -i -e "s/debug : True/debug : False/g" "$SEARX_SETTINGS"
EOF
    uWSGI_restart
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

    if user_is_available; then
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

    if ! service_is_available "http://$SEARX_INTERNAL_URL"; then
        err_msg "uWSGI app (service) at http://$SEARX_INTERNAL_URL is not available!"
    fi

    if ! service_is_available "${PUBLIC_URL}"; then
        err_msg "Public service at ${PUBLIC_URL} is not available!"
    fi

    local _debug_on
    if ask_yn "Enable searx debug mode?"; then
        enable_debug
        _debug_on=1
    fi
    echo
    systemctl --no-pager -l status uwsgi.service
    echo
    read -r -s -n1 -t 2  -p "// use CTRL-C to stop monitoring the log"
    echo
    while true;  do
        trap break 2
        #journalctl -f -u uwsgi.service
        tail -f /var/log/uwsgi/app/searx.log
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

# ----------------------------------------------------------------------------
main "$@"
# ----------------------------------------------------------------------------
