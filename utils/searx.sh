#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh -*-
# shellcheck disable=SC2119

# shellcheck source=utils/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

# ----------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------

SERVICE_NAME="searx"
SERVICE_USER="${SERVICE_NAME}"
# shellcheck disable=SC2034
SERVICE_GROUP="${SERVICE_USER}"
SERVICE_HOME="/home/${SERVICE_USER}"

SEARX_GIT_URL="https://github.com/asciimoo/searx.git"
SEARX_GIT_BRANCH="origin/master"

# FIXME: Arch Linux & RHEL should be added

SEARX_APT_PACKAGES="\
libapache2-mod-uwsgi uwsgi uwsgi-plugin-python3 \
  git build-essential libxslt-dev python3-dev python3-babel zlib1g-dev \
  libffi-dev libssl-dev"

SEARX_VENV="${SEARX_HOME}/searx-venv"
SEARX_SRC="${SEARX_HOME}/searx-src"
SEARX_SETTINGS="${SEARX_SRC}/searx/settings.yml"
SEARX_INSTANCE_NAME="${SEARX_INSTANCE_NAME:-searx@$(uname -n)}"
SEARX_UWSGI_APP="${uWSGI_SETUP}/apps-available/searx.ini"

# shellcheck disable=SC2034
CONFIG_FILES=(
    "${SEARX_UWSGI_APP}"
)

# shellcheck disable=SC2034
CONFIG_BACKUP_ENCRYPTED=(
    "${SEARX_SETTINGS}"
)

# ----------------------------------------------------------------------------
usage(){
# ----------------------------------------------------------------------------

    # shellcheck disable=SC1117
    cat <<EOF

usage:

  $(basename "$0") shell
  $(basename "$0") install    [all|user]
  $(basename "$0") update     [searx]
  $(basename "$0") remove     [all]
  $(basename "$0") activate   [service]
  $(basename "$0") deactivate [service]
  $(basename "$0") show       [service]

shell
  start interactive shell from user ${SERVICE_USER}
install / remove all
  complete setup of searx service
update searx
  Update searx installation of user ${SERVICE_USER}
activate
  activate and start service daemon (systemd unit)
deactivate service
  stop and deactivate service daemon (systemd unit)
install user
  add service user '$SERVICE_USER' at $SERVICE_HOME
show service
  show service status and log
EOF
    [ ! -z ${1+x} ] &&  echo -e "$1"
}

main(){
    rst_title "$SERVICE_NAME" part

    local _usage="ERROR: unknown or missing $1 command $2"

    case $1 in
        --source-only)  ;;
        -h|--help) usage; exit 0;;

        shell)
            sudo_or_exit
            interactive_shell
            ;;
        show)
            case $2 in
                service)
                    sudo_or_exit
                    show_service
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
                searx) update_searx;;
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
        *) usage "ERROR: unknown or missing command $1"; exit 42;;
    esac
}

_service_prefix="  |$SERVICE_USER| "

install_all() {
    rst_title "Install $SERVICE_NAME (service)"
    pkg_install "$SEARX_APT_PACKAGES"
    wait_key
    assert_user
    wait_key
    clone_searx
    wait_key
    create_venv
    wait_key
    configure_searx
    wait_key
    test_local_searx
    wait_key
    install_searx_uwsgi
    wait_key

    # ToDo ...
    # install_apache_site
    # test_public_searx
    # info_msg "searX --> https://${SEARX_APACHE_DOMAIN}${SEARX_APACHE_URL}"

}

update_searx() {
    rst_title "Update searx instance"

    echo
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
cp -f ${SEARX_SETTINGS} ${SEARX_SETTINGS}.backup
git stash push -m "BACKUP -- 'update server' at ($(date))"
git checkout -b "$(basename "$SEARX_GIT_BRANCH")" --track "$SEARX_GIT_BRANCH"
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
    rst_title "De-Install $SERVICE_NAME (service)"
    remove_service
    wait_key
    remove_user
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

# shellcheck disable=SC2164
clone_searx(){
    rst_title "Clone searx sources" section
    echo
    git_clone "$SEARX_GIT_URL" "$SEARX_SRC" \
	      "$SEARX_GIT_BRANCH" "$SERVICE_USER"

    pushd "${SEARX_SRC}" > /dev/null
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 | prefix_stdout "$_service_prefix"
cd "${SEARX_SRC}"
git config user.email "$ADMIN_EMAIL"
git config user.name "$ADMIN_NAME"
git checkout "$SEARX_GIT_BRANCH"
EOF
    popd > /dev/null
}

create_venv(){
    rst_title "Create virtualenv (python)" section

    rst_para "Create venv in ${SEARX_VENV} and install needed python packages."
    echo
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
rm -rf "${SEARX_VENV}"
python3 -m venv "${SEARX_VENV}"
. ${SEARX_VENV}/bin/activate
${SEARX_SRC}/manage.sh update_packages
EOF
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
grep -qFs -- 'source ${SEARX_VENV}/bin/activate' ~/.profile \
  || echo 'source ${SEARX_VENV}/bin/activate' >> ~/.profile
EOF

}

configure_searx(){
    rst_title "Configure searx" section
    rst_para "Setup searx config located at $SEARX_SETTINGS"
    echo
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
sed -i -e "s/ultrasecretkey/$(openssl rand -hex 16)/g" "$SEARX_SETTINGS"
sed -i -e "s/{instance_name}/${SEARX_INSTANCE_NAME}/g" "$SEARX_SETTINGS"
EOF
}

test_local_searx(){
    rstHeading "Testing searx instance localy" section
    echo
    tee_stderr 0.1 <<EOF | sudo -H -u "${SERVICE_USER}" -i 2>&1 |  prefix_stdout "$_service_prefix"
cd ${SEARX_SRC}
sed -i -e "s/debug : False/debug : True/g" "$SEARX_SETTINGS"
timeout 5 python3 searx/webapp.py &
sleep 1
curl --location --verbose --head --insecure http://127.0.0.1:8888/
sed -i -e "s/debug : True/debug : False/g" "$SEARX_SETTINGS"
EOF
    waitKEY
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

activate_service () {
    rst_title "Activate $SERVICE_NAME (service)" section
    uWSGI_enable_app "$SEARX_UWSGI_APP"
}

deactivate_service () {
    rst_title "De-Activate $SERVICE_NAME (service)" section
    uWSGI_disable_app "$SEARX_UWSGI_APP"
}

interactive_shell(){
    echo "// exit with CTRL-D"
    sudo -H -u "${SERVICE_USER}" -i
}

git_diff(){
    sudo -H -u "${SERVICE_USER}" -i <<EOF
cd ${SEARX_REPO_FOLDER}
git --no-pager diff
EOF
}

show_service () {
    rst_title "service status & log"
    echo
    systemctl status uwsgi.service
    echo
    read -r -s -n1 -t 5  -p "// use CTRL-C to stop monitoring the log"
    echo
    while true;  do
        trap break 2
        journalctl -f -u uwsgi.service
    done
    return 0
}

# ----------------------------------------------------------------------------
main "$@"
# ----------------------------------------------------------------------------
