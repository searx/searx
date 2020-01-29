#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh indent-tabs-mode: nil -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# shellcheck disable=SC2119

# shellcheck source=utils/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
source_dot_config

# ----------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------

FILTRON_ETC="/etc/filtron"

FILTRON_RULES="$FILTRON_ETC/rules.json"

FILTRON_API="127.0.0.1:4005"
FILTRON_LISTEN="127.0.0.1:4004"
FILTRON_TARGET="127.0.0.1:8888"

SERVICE_NAME="filtron"
SERVICE_USER="${SERVICE_NAME}"
SERVICE_HOME="/home/${SERVICE_USER}"
SERVICE_SYSTEMD_UNIT="${SYSTEMD_UNITS}/${SERVICE_NAME}.service"

# shellcheck disable=SC2034
SERVICE_GROUP="${SERVICE_USER}"

GO_ENV="${SERVICE_HOME}/.go_env"
GO_PKG_URL="https://dl.google.com/go/go1.13.5.linux-amd64.tar.gz"
GO_TAR=$(basename "$GO_PKG_URL")

# Apache Settings

APACHE_FILTRON_SITE="searx.conf"

# shellcheck disable=SC2034
CONFIG_FILES=(
    "${FILTRON_RULES}"
    "${SERVICE_SYSTEMD_UNIT}"
)

# ----------------------------------------------------------------------------
usage() {
# ----------------------------------------------------------------------------

    # shellcheck disable=SC1117
    cat <<EOF

usage:

  $(basename "$0") shell
  $(basename "$0") install    [all|user]
  $(basename "$0") update     [filtron]
  $(basename "$0") remove     [all]
  $(basename "$0") activate   [service]
  $(basename "$0") deactivate [service]
  $(basename "$0") inspect    [service]
  $(basename "$0") apache     [install|remove]


shell
  start interactive shell from user ${SERVICE_USER}
install / remove
  all:        complete setup of filtron service
  user:       add/remove service user '$SERVICE_USER' at $SERVICE_HOME
update filtron
  Update filtron installation of user ${SERVICE_USER}
activate service
  activate and start service daemon (systemd unit)
deactivate service
  stop and deactivate service daemon (systemd unit)
inspect service
  show service status and log
apache
  install: apache site with a reverse proxy (ProxyPass)
  remove:  apache site ${APACHE_FILTRON_SITE}

If needed change the environment variable PUBLIC_URL of your WEB service in the
${DOT_CONFIG#"$REPO_ROOT/"} file:

  PUBLIC_URL : ${PUBLIC_URL}

EOF
    [ ! -z ${1+x} ] &&  echo -e "$1"
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
                *) usage "$_usage"; exit 42;;
            esac ;;
        update)
            sudo_or_exit
            case $2 in
                filtron) update_filtron ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        remove)
            sudo_or_exit
            case $2 in
                all) remove_all;;
                user) remove_user ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        activate)
            sudo_or_exit
            case $2 in
                service)  activate_service ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        deactivate)
            sudo_or_exit
            case $2 in
                service)  deactivate_service ;;
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

install_all() {
    rst_title "Install $SERVICE_NAME (service)"
    assert_user
    wait_key
    install_go
    wait_key
    install_filtron
    wait_key
    install_service
    wait_key
    echo
    if ! service_is_available "http://${FILTRON_LISTEN}" ; then
        err_msg "Filtron does not listening on: http://${FILTRON_LISTEN}"
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

    remove_service
    wait_key
    remove_user
    rm -r "$FILTRON_ETC" 2>&1 | prefix_stdout
    wait_key
}

install_service() {
    rst_title "Install System-D Unit ${SERVICE_NAME}.service" section
    echo
    install_template "${SERVICE_SYSTEMD_UNIT}" root root 644
    wait_key
    activate_service
}

remove_service() {
    if ! ask_yn "Do you really want to deinstall $SERVICE_NAME?"; then
        return
    fi
    deactivate_service
    rm "${SERVICE_SYSTEMD_UNIT}"  2>&1 | prefix_stdout
}

activate_service() {
    rst_title "Activate $SERVICE_NAME (service)" section
    echo
    tee_stderr <<EOF | bash 2>&1
systemctl enable $SERVICE_NAME.service
systemctl restart $SERVICE_NAME.service
EOF
    tee_stderr <<EOF | bash 2>&1
systemctl status --no-pager $SERVICE_NAME.service
EOF
}

deactivate_service() {
    rst_title "De-Activate $SERVICE_NAME (service)" section
    echo
    tee_stderr <<EOF | bash 2>&1 | prefix_stdout
systemctl stop $SERVICE_NAME.service
systemctl disable $SERVICE_NAME.service
EOF
}

user_is_available() {
    sudo -i -u "$SERVICE_USER" echo \$HOME &>/dev/null
}

assert_user() {
    rst_title "user $SERVICE_USER" section
    echo
    tee_stderr 1 <<EOF | bash | prefix_stdout
sudo -H adduser --shell /bin/bash --system --home $SERVICE_HOME \
    --disabled-password --group --gecos 'Filtron' $SERVICE_USER
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

    tee_stderr <<EOF | sudo -i -u $SERVICE_USER
grep -qFs -- 'source $GO_ENV' ~/.profile || echo 'source $GO_ENV' >> ~/.profile
EOF
}

remove_user() {
    rst_title "Drop $SERVICE_USER HOME" section
    if ask_yn "Do you really want to drop $SERVICE_USER home folder?"; then
        userdel -r -f "$SERVICE_USER" 2>&1 | prefix_stdout
    else
        rst_para "Leave HOME folder $(du -sh "$SERVICE_HOME") unchanged."
    fi
}

interactive_shell(){
    echo "// exit with CTRL-D"
    sudo -H -u ${SERVICE_USER} -i
}

_service_prefix="  |$SERVICE_USER| "

go_is_available() {
    sudo -i -u "$SERVICE_USER" which go &>/dev/null
}

install_go() {
    rst_title "Install Go in user's HOME" section

    rst_para "download and install go binary .."
    cache_download "${GO_PKG_URL}" "${GO_TAR}"

    tee_stderr 0.1 <<EOF | sudo -i -u "$SERVICE_USER" | prefix_stdout "$_service_prefix"
echo \$PATH
echo \$GOPATH
mkdir -p \$HOME/local
rm -rf \$HOME/local/go
tar -C \$HOME/local -xzf ${CACHE}/${GO_TAR}
EOF
    sudo -i -u "$SERVICE_USER" <<EOF | prefix_stdout
! which go >/dev/null &&  echo "ERROR - Go Installation not found in PATH!?!"
which go >/dev/null &&  go version && echo "congratulations -- Go installation OK :)"
EOF
}

filtron_is_installed() {
    [[ -f $SERVICE_HOME/go-apps/bin/filtron ]]
}

install_filtron() {
    rst_title "Install filtron in user's ~/go-apps" section
    echo
    tee_stderr <<EOF | sudo -i -u "$SERVICE_USER" 2>&1 | prefix_stdout "$_service_prefix"
go get -v -u github.com/asciimoo/filtron
EOF
    install_template --no-eval "$FILTRON_RULES" root root 644
}

update_filtron() {
    rst_title "Update filtron" section
    echo
    tee_stderr <<EOF | sudo -i -u "$SERVICE_USER" 2>&1 | prefix_stdout "$_service_prefix"
go get -v -u github.com/asciimoo/filtron
EOF
}

inspect_service() {

    rst_title "service status & log"

    cat <<EOF

sourced ${DOT_CONFIG#"$REPO_ROOT/"} :

  PUBLIC_URL          : ${PUBLIC_URL}
  FILTRON_API         : ${FILTRON_API}
  FILTRON_LISTEN      : ${FILTRON_LISTEN}
  FILTRON_TARGET      : ${FILTRON_TARGET}

EOF

    apache_is_installed && info_msg "Apache is installed."

    if user_is_available; then
        info_msg "service account $SERVICE_USER available."
    else
        err_msg "service account $SERVICE_USER not available!"
    fi
    if go_is_available; then
        info_msg "~$SERVICE_USER: go is installed"
    else
        err_msg "~$SERVICE_USER: go is not installed"
    fi
    if filtron_is_installed; then
        info_msg "~$SERVICE_USER: filtron app is installed"
    else
        err_msg "~$SERVICE_USER: filtron app is not installed!"
    fi

    if ! service_is_available "http://${FILTRON_API}"; then
        err_msg "API not available at: http://${FILTRON_API}"
    fi

    if ! service_is_available "http://${FILTRON_LISTEN}" ; then
        err_msg "Filtron does not listening on: http://${FILTRON_LISTEN}"
    fi

    if ! service_is_available ""http://${FILTRON_TARGET}"" ; then
        info_msg "Filtron's target is available at: http://${FILTRON_TARGET}"
    fi

    if ! service_is_available "${PUBLIC_URL}"; then
        err_msg "Public service at ${PUBLIC_URL} is not available!"
    fi

    wait_key
    echo
    systemctl --no-pager -l status filtron.service
    echo
    read -r -s -n1 -t 2  -p "// use CTRL-C to stop monitoring the log"
    echo
    while true;  do
        trap break 2
        journalctl -f -u filtron
    done
    return 0
}

install_apache_site() {

    rst_title "Install Apache site $APACHE_FILTRON_SITE"

    rst_para "\
This installs a reverse proxy (ProxyPass) into apache site (${APACHE_FILTRON_SITE})"

    ! apache_is_installed && err_msg "Apache is not installed."

    if ! ask_yn "Do you really want to continue?"; then
        return
    fi

    a2enmod proxy
    a2enmod proxy_http

    echo
    apache_install_site --variant=filtron "${APACHE_FILTRON_SITE}"

    info_msg "testing public url .."
    if ! service_is_available "${PUBLIC_URL}"; then
        err_msg "Public service at ${PUBLIC_URL} is not available!"
    fi
}

remove_apache_site() {

    rst_title "Remove Apache site $APACHE_FILTRON_SITE"

    rst_para "\
This removes apache site ${APACHE_FILTRON_SITE}."

    ! apache_is_installed && err_msg "Apache is not installed."

    if ! ask_yn "Do you really want to continue?"; then
        return
    fi

    apache_remove_site "$APACHE_FILTRON_SITE"
}

# ----------------------------------------------------------------------------
main "$@"
# ----------------------------------------------------------------------------
