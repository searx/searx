#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh -*-
# shellcheck disable=SC2119

# shellcheck source=utils/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

# ----------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------

FILTRON_ETC="/etc/filtron"

SERVICE_NAME="filtron"
SERVICE_USER="${SERVICE_NAME}"
SERVICE_HOME="/home/${SERVICE_USER}"
SERVICE_SYSTEMD_UNIT="${SYSTEMD_UNITS}/${SERVICE_NAME}.service"

# shellcheck disable=SC2034
SERVICE_GROUP="${SERVICE_USER}"

GO_ENV="${SERVICE_HOME}/.go_env"
GO_PKG_URL="https://dl.google.com/go/go1.13.5.linux-amd64.tar.gz"
GO_TAR=$(basename "$GO_PKG_URL")

# ----------------------------------------------------------------------------
usage(){
# ----------------------------------------------------------------------------

    # shellcheck disable=SC1117
    cat <<EOF

usage:

  $(basename "$0") shell
  $(basename "$0") install    [all|user]
  $(basename "$0") remove     [all]
  $(basename "$0") activate   [server]
  $(basename "$0") deactivate [server]

shell        - start interactive shell with user ${SERVICE_USER}
install user - add service user '$SERVICE_USER' at $SERVICE_HOME

EOF
    [ ! -z ${1+x} ] &&  echo -e "$1"
}

main(){
    rst_title "$SERVICE_NAME" part

    local _usage="ERROR: unknown or missing $1 command $2"

    case $1 in
	--source-only)  ;;
        -h|--help) usage ;;

	shell)
	    sudo_or_exit
	    interactive_shell
	    ;;
        install)
            sudo_or_exit
            case $2 in
                all) install_all ;;
		user) assert_user ;;
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
                server)  activate_server ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        deactivate)
            sudo_or_exit
            case $2 in
                server)  deactivate_server ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        *) usage "ERROR: unknown or missing command $1"; exit 42;;
    esac
}

install_all() {
    rst_title "Install $SERVICE_NAME (service)"
    assert_user
    install_go
    install_filtron
    install_server
}

remove_all() {
    rst_title "De-Install $SERVICE_NAME (service)"
    remove_server
    remove_user
    rm -rf "$FILTRON_ETC"
    wait_key
}

install_server() {
    rst_title "Install System-D Unit ${SERVICE_NAME}.service ..." section
    install_template ${SERVICE_SYSTEMD_UNIT} root root 644
    wait_key
    activate_server
}

remove_server() {
    if ! ask_yn "Do you really want to deinstall $SERVICE_NAME?"; then
        return
    fi
    deactivate_server
    rm "${SERVICE_SYSTEMD_UNIT}"
}


activate_server () {
    rst_title "Activate $SERVICE_NAME (service)" section
    tee_stderr <<EOF | bash 2>&1 | prefix_stdout
systemctl enable $SERVICE_NAME.service
systemctl restart $SERVICE_NAME.service
EOF
    tee_stderr <<EOF | bash 2>&1 | prefix_stdout
systemctl status $SERVICE_NAME.service
EOF
    wait_key
}

deactivate_server () {
    rst_title "De-Activate $SERVICE_NAME (service)" section
    echo
    tee_stderr <<EOF | bash 2>&1 | prefix_stdout
systemctl stop $SERVICE_NAME.service
systemctl disable $SERVICE_NAME.service
EOF
    wait_key
}

assert_user() {
    rst_title "user $SERVICE_USER" section
    echo
    tee_stderr 1 <<EOF | bash | prefix_stdout
sudo -H adduser --shell /bin/bash --system --home $SERVICE_HOME --group --gecos 'Filtron' $SERVICE_USER
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
        userdel -r -f "$SERVICE_USER"
    else
        rst_para "Leave HOME folder $(du -sh "$SERVICE_HOME") unchanged."
    fi
}

interactive_shell(){
    echo "// exit with STRG-D"
    sudo -H -u ${SERVICE_USER} -i
}

_service_prefix="$SERVICE_USER@$(hostname) -->| "

install_go(){
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
    echo
    sudo -i -u "$SERVICE_USER" <<EOF | prefix_stdout
! which go >/dev/null &&  echo "Go Installation not found in PATH!?!"
which go >/dev/null &&  go version && echo "congratulations -- Go installation OK :)"
EOF
    wait_key
}

install_filtron() {
    tee_stderr <<EOF | sudo -i -u "$SERVICE_USER" | prefix_stdout "$_service_prefix"
go get -v -u github.com/asciimoo/filtron 2>&1
EOF
    install_template "$FILTRON_ETC/rules.json" root root 644
}

# ----------------------------------------------------------------------------
main "$@"
# ----------------------------------------------------------------------------
