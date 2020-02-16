#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh indent-tabs-mode: nil -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

# shellcheck source=utils/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
source_dot_config

# ----------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------

PUBLIC_URL_PATH_MORTY="/morty"
PUBLIC_URL_MORTY="$(dirname "${PUBLIC_URL}")${PUBLIC_URL_PATH_MORTY}"

MORTY_LISTEN="${MORTY_LISTEN:-127.0.0.1:3000}"
# shellcheck disable=SC2034
MORTY_TIMEOUT=5

SERVICE_NAME="morty"
SERVICE_USER="${SERVICE_USER:-${SERVICE_NAME}}"
SERVICE_HOME_BASE="${SERVICE_HOME_BASE:-/usr/local}"
SERVICE_HOME="${SERVICE_HOME_BASE}/${SERVICE_USER}"
SERVICE_SYSTEMD_UNIT="${SYSTEMD_UNITS}/${SERVICE_NAME}.service"
# shellcheck disable=SC2034
SERVICE_GROUP="${SERVICE_USER}"
# shellcheck disable=SC2034
SERVICE_ENV_DEBUG=false

GO_ENV="${SERVICE_HOME}/.go_env"
GO_PKG_URL="https://dl.google.com/go/go1.13.5.linux-amd64.tar.gz"
GO_TAR=$(basename "$GO_PKG_URL")

# shellcheck disable=SC2034
CONFIG_FILES=()

# Apache Settings

APACHE_MORTY_SITE="morty.conf"

# ----------------------------------------------------------------------------
usage() {
# ----------------------------------------------------------------------------

    # shellcheck disable=SC1117
    cat <<EOF

usage::

  $(basename "$0") shell
  $(basename "$0") install    [all|user]
  $(basename "$0") update     [morty]
  $(basename "$0") remove     [all]
  $(basename "$0") activate   [service]
  $(basename "$0") deactivate [service]
  $(basename "$0") inspect    [service]
  $(basename "$0") option     [debug-on|debug-off]
  $(basename "$0") apache     [install|remove]
  $(basename "$0") info       [searx]

shell
  start interactive shell from user ${SERVICE_USER}
install / remove
  all:        complete setup of morty service
  user:       add/remove service user '$SERVICE_USER' ($SERVICE_HOME)
update morty
  Update morty installation ($SERVICE_HOME)
activate service
  activate and start service daemon (systemd unit)
deactivate service
  stop and deactivate service daemon (systemd unit)
inspect service
  show service status and log
option
  set one of the available options
apache : ${PUBLIC_URL_MORTY}
  :install: apache site with a reverse proxy (ProxyPass)
  :remove:  apache site ${APACHE_MORTY_SITE}

If needed, set the environment variable MORTY_LISTEN in the
${DOT_CONFIG#"$REPO_ROOT/"} file::

  MORTY_LISTEN :   ${MORTY_LISTEN}
  SERVICE_USER :   ${SERVICE_USER}
EOF
    info_searx
    [[ -n ${1} ]] &&  err_msg "$1"
}

info_searx() {
    # shellcheck disable=SC1117
    cat <<EOF

To activate morty in searx, add result_proxy to your settings.yml::

  result_proxy:
      url : ${PUBLIC_URL_MORTY}/

further read: ${DOCS_URL}/admin/morty.html

EOF
}

main() {
    rst_title "$SERVICE_NAME" part

    required_commands \
        dpkg apt-get install git wget curl \
        || exit

    local _usage="ERROR: unknown or missing $1 command $2"

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
                *) usage "$_usage"; exit 42;;
            esac ;;
        update)
            sudo_or_exit
            case $2 in
                morty) update_morty ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        remove)
            sudo_or_exit
            case $2 in
                all) remove_all;;
                user) drop_service_account "${SERVICE_USER}" ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        activate)
            sudo_or_exit
            case $2 in
                service)  systemd_activate_service "${SERVICE_NAME}" ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        deactivate)
            sudo_or_exit
            case $2 in
                service)  systemd_deactivate_service "${SERVICE_NAME}" ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        apache)
            sudo_or_exit
            case $2 in
                install) install_apache_site ;;
                remove) remove_apache_site ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        info)
            case $2 in
                searx) info_searx ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        option)
            sudo_or_exit
            case $2 in
                debug-on)  enable_debug ;;
                debug-off)  disable_debug ;;
                *) usage "$_usage"; exit 42;;
            esac ;;

        *) usage "ERROR: unknown or missing command $1"; exit 42;;
    esac
}

install_all() {
    rst_title "Install $SERVICE_NAME (service)"
    assert_user
    wait_key
    install_go "${GO_PKG_URL}" "${GO_TAR}" "${SERVICE_USER}"
    wait_key
    install_morty
    wait_key
    systemd_install_service "${SERVICE_NAME}" "${SERVICE_SYSTEMD_UNIT}"
    wait_key
    info_searx
    if ! service_is_available "http://${MORTY_LISTEN}" ; then
        err_msg "Morty does not listening on: http://${MORTY_LISTEN}"
    fi
    if apache_is_installed; then
        info_msg "Apache is installed on this host."
        if ask_yn "Do you want to install a reverse proxy (ProxyPass)" Yn; then
            install_apache_site
        fi
    fi
    if ask_yn "Do you want to inspect the installation?" Yn; then
        inspect_service
    fi

}

remove_all() {
    rst_title "De-Install $SERVICE_NAME (service)"

    rst_para "\
It goes without saying that this script can only be used to remove
installations that were installed with this script."

    if systemd_remove_service "${SERVICE_NAME}" "${SERVICE_SYSTEMD_UNIT}"; then
        drop_service_account "${SERVICE_USER}"
    fi
}

assert_user() {
    rst_title "user $SERVICE_USER" section
    echo
    tee_stderr 1 <<EOF | bash | prefix_stdout
sudo -H adduser --shell /bin/bash --system --home $SERVICE_HOME \
    --disabled-password --group --gecos 'Morty' $SERVICE_USER
sudo -H usermod -a -G shadow $SERVICE_USER
groups $SERVICE_USER
EOF
    SERVICE_HOME="$(sudo -i -u "$SERVICE_USER" echo \$HOME)"
    export SERVICE_HOME
    echo "export SERVICE_HOME=$SERVICE_HOME"

    cat > "$GO_ENV" <<EOF
export GOPATH=\$HOME/go-apps
export PATH=\$PATH:\$HOME/local/go/bin:\$GOPATH/bin
EOF
    echo "Environment $GO_ENV has been setup."

    tee_stderr <<EOF | sudo -i -u "$SERVICE_USER"
grep -qFs -- 'source $GO_ENV' ~/.profile || echo 'source $GO_ENV' >> ~/.profile
EOF
}

morty_is_installed() {
    [[ -f $SERVICE_HOME/go-apps/bin/morty ]]
}

_svcpr="  |${SERVICE_USER}| "

install_morty() {
    rst_title "Install morty in user's ~/go-apps" section
    echo
    tee_stderr <<EOF | sudo -i -u "$SERVICE_USER" 2>&1 | prefix_stdout "$_svcpr"
go get -v -u github.com/asciimoo/morty
EOF
    tee_stderr <<EOF | sudo -i -u "$SERVICE_USER" 2>&1 | prefix_stdout "$_svcpr"
cd \$GOPATH/src/github.com/asciimoo/morty
go test
go test -benchmem -bench .
EOF
}

update_morty() {
    rst_title "Update morty" section
    echo
    tee_stderr <<EOF | sudo -i -u "$SERVICE_USER" 2>&1 | prefix_stdout "$_svcpr"
go get -v -u github.com/asciimoo/morty
EOF
    tee_stderr <<EOF | sudo -i -u "$SERVICE_USER" 2>&1 | prefix_stdout "$_svcpr"
cd \$GOPATH/src/github.com/asciimoo/morty
go test
go test -benchmem -bench .
EOF
}

set_service_env_debug() {

    # usage:  set_service_env_debug [false|true]

    # shellcheck disable=SC2034
    local SERVICE_ENV_DEBUG="${1:-false}"
    if systemd_remove_service "${SERVICE_NAME}" "${SERVICE_SYSTEMD_UNIT}"; then
        systemd_install_service "${SERVICE_NAME}" "${SERVICE_SYSTEMD_UNIT}"
    fi
}

inspect_service() {

    rst_title "service status & log"

    cat <<EOF

sourced ${DOT_CONFIG#"$REPO_ROOT/"} :

  MORTY_LISTEN :   ${MORTY_LISTEN}

EOF

    if service_account_is_available "$SERVICE_USER"; then
        info_msg "service account $SERVICE_USER available."
    else
        err_msg "service account $SERVICE_USER not available!"
    fi
    if go_is_available "$SERVICE_USER"; then
        info_msg "~$SERVICE_USER: go is installed"
    else
        err_msg "~$SERVICE_USER: go is not installed"
    fi
    if morty_is_installed; then
        info_msg "~$SERVICE_USER: morty app is installed"
    else
        err_msg "~$SERVICE_USER: morty app is not installed!"
    fi

    if ! service_is_available "http://${MORTY_LISTEN}" ; then
        err_msg "Morty does not listening on: http://${MORTY_LISTEN}"
        echo -e "${_Green}stop with [${_BCyan}CTRL-C${_Green}] or .."
        wait_key
    fi

    local _debug_on
    if ask_yn "Enable filtron debug mode?"; then
        enable_debug
        _debug_on=1
    fi

    echo
    systemctl --no-pager -l status "${SERVICE_NAME}"
    echo

    info_msg "morty URL --> http://${MORTY_LISTEN}"
    info_msg "public URL --> ${PUBLIC_URL_MORTY}"
    # shellcheck disable=SC2059
    printf "// use ${_BCyan}CTRL-C${_creset} to stop monitoring the log"
    read -r -s -n1 -t 2
    echo
    while true;  do
        trap break 2
        journalctl -f -u "${SERVICE_NAME}"
    done

    if [[ $_debug_on == 1 ]]; then
        FORCE_SELECTION=Y disable_debug
    fi
    return 0
}


enable_debug() {
    warn_msg "Do not enable debug in production enviroments!!"
    info_msg "Enabling debug option needs to reinstall systemd service!"
    set_service_env_debug true
}

disable_debug() {
    info_msg "Disabling debug option needs to reinstall systemd service!"
    set_service_env_debug false
}

install_apache_site() {

    rst_title "Install Apache site $APACHE_MORTY_SITE"

    rst_para "\
This installs a reverse proxy (ProxyPass) into apache site (${APACHE_MORTY_SITE})"

    ! apache_is_installed && err_msg "Apache is not installed."

    if ! ask_yn "Do you really want to continue?"; then
        return
    fi

    a2enmod headers
    a2enmod proxy
    a2enmod proxy_http

    echo
    apache_install_site "${APACHE_MORTY_SITE}"

    info_msg "testing public url .."
    if ! service_is_available "${PUBLIC_URL_MORTY}"; then
        err_msg "Public service at ${PUBLIC_URL_MORTY} is not available!"
    fi
}

remove_apache_site() {

    rst_title "Remove Apache site $APACHE_MORTY_SITE"

    rst_para "\
This removes apache site ${APACHE_MORTY_SITE}."

    ! apache_is_installed && err_msg "Apache is not installed."

    if ! ask_yn "Do you really want to continue?"; then
        return
    fi

    apache_remove_site "$APACHE_MORTY_SITE"
}
# ----------------------------------------------------------------------------
main "$@"
# ----------------------------------------------------------------------------
