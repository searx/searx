#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh indent-tabs-mode: nil -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# shellcheck disable=SC2059,SC1117

# ubuntu, debian, arch, fedora ...
DIST_ID=$(source /etc/os-release; echo "$ID");
# shellcheck disable=SC2034
DIST_VERS=$(source /etc/os-release; echo "$VERSION_ID");

ADMIN_NAME="${ADMIN_NAME:-$(git config user.name)}"
ADMIN_NAME="${ADMIN_NAME:-$USER}"

ADMIN_EMAIL="${ADMIN_EMAIL:-$(git config user.email)}"
ADMIN_EMAIL="${ADMIN_EMAIL:-$USER@$(hostname)}"

if [[ -z "${REPO_ROOT}" ]]; then
    REPO_ROOT=$(dirname "${BASH_SOURCE[0]}")
    while [ -h "${REPO_ROOT}" ] ; do
        REPO_ROOT=$(readlink "${REPO_ROOT}")
    done
    REPO_ROOT=$(cd "${REPO_ROOT}/.." && pwd -P )
fi

if [[ -z ${TEMPLATES} ]]; then
    TEMPLATES="${REPO_ROOT}/utils/templates"
fi

if [[ -z "$CACHE" ]]; then
    CACHE="${REPO_ROOT}/cache"
fi

if [[ -z ${DIFF_CMD} ]]; then
    DIFF_CMD="diff -u"
    if command -v colordiff >/dev/null;  then
        DIFF_CMD="colordiff -u"
    fi
fi

DOT_CONFIG="${DOT_CONFIG:-${REPO_ROOT}/.config.sh}"

source_dot_config() {
    if [[ ! -e "${DOT_CONFIG}" ]]; then
        err_msg "configuration does not extsts at: ${DOT_CONFIG}"
        return 42
    fi
    # shellcheck disable=SC1090
    source "${DOT_CONFIG}"
}

sudo_or_exit() {
    # usage: sudo_or_exit

    if [ ! "$(id -u)" -eq 0 ];  then
        err_msg "this command requires root (sudo) privilege!" >&2
        exit 42
    fi
}

required_commands() {

    # usage:  required_commands [cmd1 ...]

    local exit_val=0
    while [ -n "$1" ]; do

        if ! command -v "$1" &>/dev/null; then
            err_msg "missing command $1"
            exit_val=42
        fi
        shift
    done
    return $exit_val
}

# colors
# ------

# shellcheck disable=SC2034
set_terminal_colors() {
    _colors=8
    _creset='\e[0m'  # reset all attributes

    _Black='\e[0;30m'
    _White='\e[1;37m'
    _Red='\e[0;31m'
    _Green='\e[0;32m'
    _Yellow='\e[0;33m'
    _Blue='\e[0;34m'
    _Violet='\e[0;35m'
    _Cyan='\e[0;36m'

    _BBlack='\e[1;30m'
    _BWhite='\e[1;37m'
    _BRed='\e[1;31m'
    _BGreen='\e[1;32m'
    _BYellow='\e[1;33m'
    _BBlue='\e[1;34m'
    _BPurple='\e[1;35m'
    _BCyan='\e[1;36m'
}

if [ ! -p /dev/stdout ]; then
    set_terminal_colors
fi

# reST
# ----

if command -v fmt >/dev/null; then
    export FMT="fmt -u"
else
    export FMT="cat"
fi

rst_title() {
    # usage: rst_title <header-text> [part|chapter|section]

    case ${2-chapter} in
        part)     printf "\n${_BGreen}${1//?/=}${_creset}\n${_BCyan}${1}${_creset}\n${_BGreen}${1//?/=}${_creset}\n";;
        chapter)  printf "\n${_BCyan}${1}${_creset}\n${_BGreen}${1//?/=}${_creset}\n";;
        section)  printf "\n${_BCyan}${1}${_creset}\n${_BGreen}${1//?/-}${_creset}\n";;
        *)
            err_msg "invalid argument '${2}' in line $(caller)"
            return 42
            ;;
    esac
}

rst_para() {
    # usage:  RST_INDENT=1 rst_para "lorem ipsum ..."
    local prefix=''
    if [[ -n $RST_INDENT ]] && [[ $RST_INDENT -gt 0 ]]; then
        prefix="$(for i in $(seq 1 "$RST_INDENT"); do printf "  "; done)"
        echo -en "\n$*\n" | $FMT | prefix_stdout "$prefix"
    else
        echo -en "\n$*\n" | $FMT
    fi
}

die() {
    echo -e "${_BRed}ERROR:${_creset} ${BASH_SOURCE[1]}: line ${BASH_LINENO[0]}: ${2-died ${1-1}}" >&2;
    exit "${1-1}"
}

die_caller() {
    echo -e "${_BRed}ERROR:${_creset} ${BASH_SOURCE[2]}: line ${BASH_LINENO[1]}: ${FUNCNAME[1]}(): ${2-died ${1-1}}" >&2;
    exit "${1-1}"
}

err_msg()  { echo -e "${_BRed}ERROR:${_creset} $*" >&2; }
warn_msg() { echo -e "${_BBlue}WARN:${_creset}  $*" >&2; }
info_msg() { echo -e "${_BYellow}INFO:${_creset}  $*" >&2; }

clean_stdin() {
    if [[ $(uname -s) != 'Darwin' ]]; then
        while read -r -n1 -t 0.1; do : ; done
    fi
}

wait_key(){
    # usage: waitKEY [<timeout in sec>]

    clean_stdin
    local _t=$1
    local msg="${MSG}"
    [[ -z "$msg" ]] && msg="${_Green}** press any [${_BCyan}KEY${_Green}] to continue **${_creset}"

    [[ -n $FORCE_TIMEOUT ]] && _t=$FORCE_TIMEOUT
    [[ -n $_t ]] && _t="-t $_t"
    printf "$msg"
    # shellcheck disable=SC2086
    read -r -s -n1 $_t
    echo
    clean_stdin
}

ask_yn() {
    # usage: ask_yn <prompt-text> [Ny|Yn] [<timeout in sec>]

    local EXIT_YES=0 # exit status 0 --> successful
    local EXIT_NO=1  # exit status 1 --> error code

    local _t=$3
    [[ -n $FORCE_TIMEOUT ]] && _t=$FORCE_TIMEOUT
    [[ -n $_t ]] && _t="-t $_t"
    case "${FORCE_SELECTION:-${2}}" in
        Y) return ${EXIT_YES} ;;
        N) return ${EXIT_NO} ;;
        Yn)
            local exit_val=${EXIT_YES}
            local choice="[${_BGreen}YES${_creset}/no]"
            local default="Yes"
            ;;
        *)
            local exit_val=${EXIT_NO}
            local choice="[${_BGreen}NO${_creset}/yes]"
            local default="No"
            ;;
    esac
    echo
    while true; do
        clean_stdin
        printf "$1 ${choice} "
        # shellcheck disable=SC2086
        read -r -n1 $_t
        if [[ -z $REPLY ]]; then
            printf "$default\n"; break
        elif [[ $REPLY =~ ^[Yy]$ ]]; then
            exit_val=${EXIT_YES}
            printf "\n"
            break
        elif [[ $REPLY =~ ^[Nn]$ ]]; then
            exit_val=${EXIT_NO}
            printf "\n"
            break
        fi
        _t=""
        err_msg "invalid choice"
    done
    clean_stdin
    return $exit_val
}

tee_stderr () {

    # usage::
    #   tee_stderr 1 <<EOF | python -i
    #   print("hello")
    #   EOF
    #   ...
    #   >>> print("hello")
    #    hello

    local _t="0";
    if [[ -n $1 ]] ; then _t="$1"; fi

    (while read -r line; do
         # shellcheck disable=SC2086
         sleep $_t
         echo -e "$line" >&2
         echo "$line"
    done)
}

prefix_stdout () {
    # usage: <cmd> | prefix_stdout [prefix]

    local prefix="${_BYellow}-->|${_creset}"

    if [[ -n $1 ]] ; then prefix="$1"; fi

    # shellcheck disable=SC2162
    (while IFS= read line; do
        echo -e "${prefix}$line"
    done)
}

append_line() {

    # usage: append_line <line> <file>
    #
    # Append line if not exists, create file if not exists. E.g::
    #
    #     append_line 'source ~/.foo' ~/bashrc

    local LINE=$1
    local FILE=$2
    grep -qFs -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
}

cache_download() {

    # usage: cache_download <url> <local-filename>

    local exit_value=0

    if [[ -n ${SUDO_USER} ]]; then
        sudo -u "${SUDO_USER}" mkdir -p "${CACHE}"
    else
        mkdir -p "${CACHE}"
    fi

    if [[ -f "${CACHE}/$2" ]] ; then
        info_msg "already cached: $1"
        info_msg "  --> ${CACHE}/$2"
    fi

    if [[ ! -f "${CACHE}/$2" ]]; then
        info_msg "caching: $1"
        info_msg "  --> ${CACHE}/$2"
        if [[ -n ${SUDO_USER} ]]; then
            sudo -u "${SUDO_USER}" wget --progress=bar -O "${CACHE}/$2" "$1" ; exit_value=$?
        else
            wget --progress=bar -O "${CACHE}/$2" "$1" ; exit_value=$?
        fi
        if [[ ! $exit_value = 0 ]]; then
            err_msg "failed to download: $1"
        fi
    fi
}

backup_file() {

    # usage: backup_file /path/to/file.foo

    local stamp
    stamp=$(date +"_%Y%m%d_%H%M%S")
    info_msg "create backup: ${1}${stamp}"
    cp -a "${1}" "${1}${stamp}"
}

choose_one() {

    # usage:
    #
    #   DEFAULT_SELECT= 2 \
    #     choose_one <name> "your selection?" "Coffee" "Coffee with milk"

    local default=${DEFAULT_SELECT-1}
    local REPLY
    local env_name=$1 && shift
    local choice=$1;
    local max="${#@}"
    local _t
    [[ -n $FORCE_TIMEOUT ]] && _t=$FORCE_TIMEOUT
    [[ -n $_t ]] && _t="-t $_t"

    list=("$@")
    echo -e "${_BGreen}Menu::${_creset}"
    for ((i=1; i<= $((max -1)); i++)); do
        if [[ "$i" == "$default" ]]; then
            echo -e "  ${_BGreen}$i.${_creset}) ${list[$i]} [default]"
        else
            echo -e "  $i.) ${list[$i]}"
        fi
    done
    while true; do
        clean_stdin
        printf "$1 [${_BGreen}$default${_creset}] "

        if (( 10 > max )); then
            # shellcheck disable=SC2086
            read -r -n1 $_t
        else
            # shellcheck disable=SC2086,SC2229
            read -r $_t
        fi
        # selection fits
        [[ $REPLY =~ ^-?[0-9]+$ ]] && (( REPLY > 0 )) && (( REPLY < max )) && break

        # take default
        [[ -z $REPLY ]] && REPLY=$default && break

        _t=""
        err_msg "invalid choice"
    done
    eval "$env_name"='${list[${REPLY}]}'
    echo
    clean_stdin
}

install_template() {

    # usage:
    #
    #     install_template [--no-eval] [--variant=<name>] \
    #                      {file} [{owner} [{group} [{chmod}]]]
    #
    # E.g. the origin of variant 'raw' of /etc/updatedb.conf is::
    #
    #    ${TEMPLATES}/etc/updatedb.conf:raw
    #
    # To install variant 'raw' of /etc/updatedb.conf without evaluated
    # replacements you can use::
    #
    #    install_template --variant=raw --no-eval \
    #                     /etc/updatedb.conf root root 644

    local _reply=""
    local do_eval=1
    local variant=""
    local pos_args=("$0")

    for i in "$@"; do
        case $i in
            --no-eval) do_eval=0; shift ;;
            --variant=*) variant=":${i#*=}"; shift ;;
            *) pos_args+=("$i") ;;
        esac
    done

    local dst="${pos_args[1]}"
    local template_origin="${TEMPLATES}${dst}${variant}"
    local template_file="${TEMPLATES}${dst}"

    local owner="${pos_args[2]-$(id -un)}"
    local group="${pos_args[3]-$(id -gn)}"
    local chmod="${pos_args[4]-644}"

    info_msg "install (eval=$do_eval): ${dst}"
    [[ -n $variant ]] && info_msg "variant --> ${variant}"

    if [[ ! -f "${template_origin}" ]] ; then
        err_msg "${template_origin} does not exists"
        err_msg "... can't install $dst"
        wait_key 30
        return 42
    fi

    if [[ "$do_eval" == "1" ]]; then
        template_file="${CACHE}${dst}${variant}"
        info_msg "BUILD template ${template_file}"
        if [[ -n ${SUDO_USER} ]]; then
            sudo -u "${SUDO_USER}" mkdir -p "$(dirname "${template_file}")"
        else
            mkdir -p "$(dirname "${template_file}")"
        fi
        # shellcheck disable=SC2086
        eval "echo \"$(cat ${template_origin})\"" > "${template_file}"
        if [[ -n ${SUDO_USER} ]]; then
            chown "${SUDO_USER}:${SUDO_USER}" "${template_file}"
        fi
    else
        template_file=$template_origin
    fi

    mkdir -p "$(dirname "${dst}")"

    if [[ ! -f "${dst}" ]]; then
        info_msg "install: ${template_file}"
        sudo -H install -v -o "${owner}" -g "${group}" -m "${chmod}" \
             "${template_file}" "${dst}" | prefix_stdout
        return $?
    fi

    if [[ -f "${dst}" ]] && cmp --silent "${template_file}" "${dst}" ; then
        info_msg "file ${dst} allready installed"
        return 0
    fi

    info_msg "diffrent file ${dst} allready exists on this host"

    while true; do
        choose_one _reply "choose next step with file $dst" \
                   "replace file" \
                   "leave file unchanged" \
                   "interactiv shell" \
                   "diff files"

        case $_reply in
            "replace file")
                info_msg "install: ${template_file}"
                sudo -H install -v -o "${owner}" -g "${group}" -m "${chmod}" \
                     "${template_file}" "${dst}" | prefix_stdout
                break
                ;;
            "leave file unchanged")
                break
                ;;
            "interactiv shell")
                echo -e "// edit ${_Red}${dst}${_creset} to your needs"
                echo -e "// exit with [${_BCyan}CTRL-D${_creset}]"
                sudo -H -u "${owner}" -i
                $DIFF_CMD "${dst}" "${template_file}"
                echo
                echo -e "// ${_BBlack}did you edit file ...${_creset}"
                echo -en "//  ${_Red}${dst}${_creset}"
                if ask_yn "//${_BBlack}... to your needs?${_creset}"; then
                    break
                fi
                ;;
            "diff files")
                $DIFF_CMD "${dst}" "${template_file}" | prefix_stdout
        esac
    done
}


service_is_available() {

    # usage:  service_is_available <URL>

    [[ -z $1 ]] && die_caller 42 "missing argument <URL>"
    local URL="$1"
    http_code=$(curl -H 'Cache-Control: no-cache' \
         --silent -o /dev/null --head --write-out '%{http_code}' --insecure \
         "${URL}")
    exit_val=$?
    if [[ $exit_val = 0 ]]; then
        info_msg "got $http_code from ${URL}"
    fi
    case "$http_code" in
        404|410|423) exit_val=$http_code;;
    esac
    return "$exit_val"
}

# golang
# ------

go_is_available() {

    # usage:  go_is_available $SERVICE_USER && echo "go is installed!"

    sudo -i -u "${1}" which go &>/dev/null
}

install_go() {

    # usage:  install_go "${GO_PKG_URL}" "${GO_TAR}" "${SERVICE_USER}"

    local _svcpr="  ${_Yellow}|${3}|${_creset} "

    rst_title "Install Go in user's HOME" section

    rst_para "download and install go binary .."
    cache_download "${1}" "${2}"

    tee_stderr 0.1 <<EOF | sudo -i -u "${3}" | prefix_stdout "$_svcpr"
echo \$PATH
echo \$GOPATH
mkdir -p \$HOME/local
rm -rf \$HOME/local/go
tar -C \$HOME/local -xzf ${CACHE}/${2}
EOF
    sudo -i -u "${3}" <<EOF | prefix_stdout
! which go >/dev/null &&  echo "ERROR - Go Installation not found in PATH!?!"
which go >/dev/null &&  go version && echo "congratulations -- Go installation OK :)"
EOF
}

# system accounts
# ---------------

service_account_is_available() {

    # usage:  service_account_is_available "$SERVICE_USER" && echo "OK"

    sudo -i -u "$1" echo \$HOME &>/dev/null
}

drop_service_account() {

    # usage:  drop_service_account "${SERVICE_USER}"

    rst_title "Drop ${1} HOME" section
    if ask_yn "Do you really want to drop ${1} home folder?"; then
        userdel -r -f "${1}" 2>&1 | prefix_stdout
    else
        rst_para "Leave HOME folder $(du -sh "${1}") unchanged."
    fi
}

interactive_shell(){

    # usage:  interactive_shell "${SERVICE_USER}"

    echo -e "// exit with [${_BCyan}CTRL-D${_creset}]"
    sudo -H -u "${1}" -i
}


# systemd
# -------

SYSTEMD_UNITS="${SYSTEMD_UNITS:-/lib/systemd/system}"

systemd_install_service() {

    # usage:  systemd_install_service "${SERVICE_NAME}" "${SERVICE_SYSTEMD_UNIT}"

    rst_title "Install System-D Unit ${1}" section
    echo
    install_template "${2}" root root 644
    wait_key
    systemd_activate_service "${1}"
}

systemd_remove_service() {

    # usage:  systemd_remove_service "${SERVICE_NAME}" "${SERVICE_SYSTEMD_UNIT}"

    if ! ask_yn "Do you really want to deinstall systemd unit ${1}?"; then
        return 42
    fi
    systemd_deactivate_service "${1}"
    rm "${2}"  2>&1 | prefix_stdout
}

systemd_activate_service() {

    # usage:  systemd_activate_service "${SERVICE_NAME}"

    rst_title "Activate ${1} (service)" section
    echo
    tee_stderr <<EOF | bash 2>&1
systemctl enable  ${1}.service
systemctl restart ${1}.service
EOF
    tee_stderr <<EOF | bash 2>&1
systemctl status --no-pager ${1}.service
EOF
}

systemd_deactivate_service() {

    # usage:  systemd_deactivate_service "${SERVICE_NAME}"

    rst_title "De-Activate ${1} (service)" section
    echo
    tee_stderr <<EOF | bash 2>&1 | prefix_stdout
systemctl stop    ${1}.service
systemctl disable ${1}.service
EOF
}

systemd_restart_service() {

    # usage:  systemd_restart_service "${SERVICE_NAME}"

    rst_title "Restart ${1} (service)" section
    echo
    tee_stderr <<EOF | bash 2>&1
systemctl restart ${1}.service
EOF
    tee_stderr <<EOF | bash 2>&1
systemctl status --no-pager ${1}.service
EOF
}


# nginx
# -----

nginx_distro_setup() {
    # shellcheck disable=SC2034

    NGINX_DEFAULT_SERVER=/etc/nginx/nginx.conf

    # Including *location* directives from a dedicated config-folder into the
    # server directive is, what what fedora (already) does.
    NGINX_APPS_ENABLED="/etc/nginx/default.d"

    # We add a apps-available folder and linking configurations into the
    # NGINX_APPS_ENABLED folder.  See also nginx_include_apps_enabled().
    NGINX_APPS_AVAILABLE="/etc/nginx/default.apps-available"

    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            NGINX_PACKAGES="nginx"
            NGINX_DEFAULT_SERVER=/etc/nginx/sites-available/default
            ;;
        arch-*)
            NGINX_PACKAGES="nginx-mainline"
            ;;
        fedora-*)
            NGINX_PACKAGES="nginx"
            ;;
        *)
            err_msg "$DIST_ID-$DIST_VERS: nginx not yet implemented"
            ;;
    esac
}
nginx_distro_setup

install_nginx(){
    info_msg "installing nginx ..."
    pkg_install "${NGINX_PACKAGES}"
    case $DIST_ID-$DIST_VERS in
        arch-*|fedora-*)
            systemctl enable nginx
            systemctl start nginx
            ;;
    esac
}

nginx_is_installed() {
    command -v nginx &>/dev/null
}

nginx_reload() {

    info_msg "reload nginx .."
    echo
    if ! nginx -t; then
       err_msg "testing nginx configuration failed"
       return 42
    fi
    systemctl restart nginx
}

nginx_install_app() {

    # usage:  nginx_install_app [<template option> ...] <myapp>
    #
    # <template option>:   see install_template

    local template_opts=()
    local pos_args=("$0")

    for i in "$@"; do
        case $i in
            -*) template_opts+=("$i");;
            *)  pos_args+=("$i");;
        esac
    done

    nginx_include_apps_enabled "${NGINX_DEFAULT_SERVER}"

    install_template "${template_opts[@]}" \
                     "${NGINX_APPS_AVAILABLE}/${pos_args[1]}" \
                     root root 644
    nginx_enable_app "${pos_args[1]}"
    info_msg "installed nginx app: ${pos_args[1]}"
}

nginx_include_apps_enabled() {

    # Add the *NGINX_APPS_ENABLED* infrastruture to a nginx server block.  Such
    # infrastruture is already known from fedora, including apps (location
    # directives) from the /etc/nginx/default.d folder into the *default* nginx
    # server.

    # usage: nginx_include_apps_enabled <config-file>
    #
    #   config-file: Config file with server directive in.

    [[ -z $1 ]] && die_caller 42 "missing argument <config-file>"
    local server_conf="$1"

    # include /etc/nginx/default.d/*.conf;
    local include_directive="include ${NGINX_APPS_ENABLED}/*.conf;"
    local include_directive_re="^\s*include ${NGINX_APPS_ENABLED}/\*\.conf;"

    info_msg "checking existence: '${include_directive}' in file  ${server_conf}"
    if grep "${include_directive_re}" "${server_conf}"; then
        info_msg "OK, already exists."
        return
    fi

    info_msg "add missing directive: '${include_directive}'"
    cp "${server_conf}" "${server_conf}.bak"

    (
        local line
        local stage=0
        while IFS=  read -r line
        do
            echo "$line"
            if [[ $stage = 0 ]]; then
                if [[ $line =~ ^[[:space:]]*server*[[:space:]]*\{ ]]; then
                    stage=1
                fi
            fi

            if [[ $stage = 1 ]]; then
                echo "        # Load configuration files for the default server block."
                echo "        $include_directive"
                echo ""
                stage=2
            fi
        done < "${server_conf}.bak"
    ) > "${server_conf}"

}

nginx_remove_app() {

    # usage:  nginx_remove_app <myapp.conf>

    info_msg "remove nginx app: $1"
    nginx_dissable_app "$1"
    rm -f "${NGINX_APPS_AVAILABLE}/$1"
}

nginx_enable_app() {

    # usage:  nginx_enable_app <myapp.conf>

    local CONF="$1"

    info_msg "enable nginx app: ${CONF}"
    mkdir -p "${NGINX_APPS_ENABLED}"
    rm -f "${NGINX_APPS_ENABLED}/${CONF}"
    ln -s "${NGINX_APPS_AVAILABLE}/${CONF}" "${NGINX_APPS_ENABLED}/${CONF}"
    nginx_reload
}

nginx_dissable_app() {

    # usage:  nginx_disable_app <myapp.conf>

    local CONF="$1"

    info_msg "disable nginx app: ${CONF}"
    rm -f "${NGINX_APPS_ENABLED}/${CONF}"
    nginx_reload
}


# Apache
# ------

apache_distro_setup() {
    # shellcheck disable=SC2034
    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            # debian uses the /etc/apache2 path, while other distros use
            # the apache default at /etc/httpd
            APACHE_SITES_AVAILABLE="/etc/apache2/sites-available"
            APACHE_SITES_ENABLED="/etc/apache2/sites-enabled"
            APACHE_MODULES="/usr/lib/apache2/modules"
            APACHE_PACKAGES="apache2"
            ;;
        arch-*)
            APACHE_SITES_AVAILABLE="/etc/httpd/sites-available"
            APACHE_SITES_ENABLED="/etc/httpd/sites-enabled"
            APACHE_MODULES="modules"
            APACHE_PACKAGES="apache"
            ;;
        fedora-*)
            APACHE_SITES_AVAILABLE="/etc/httpd/sites-available"
            APACHE_SITES_ENABLED="/etc/httpd/sites-enabled"
            APACHE_MODULES="modules"
            APACHE_PACKAGES="httpd"
            ;;
        *)
            err_msg "$DIST_ID-$DIST_VERS: apache not yet implemented"
            ;;
    esac
}

apache_distro_setup

install_apache(){
    info_msg "installing apache ..."
    pkg_install "$APACHE_PACKAGES"
    case $DIST_ID-$DIST_VERS in
        arch-*|fedora-*)
            if ! grep "IncludeOptional sites-enabled" "/etc/httpd/conf/httpd.conf"; then
                echo "IncludeOptional sites-enabled/*.conf" >> "/etc/httpd/conf/httpd.conf"
            fi
            systemctl enable httpd
            systemctl start httpd
            ;;
    esac
}

apache_is_installed() {
    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*) (command -v apachectl) &>/dev/null;;
        arch-*) (command -v httpd) &>/dev/null;;
        fedora-*) (command -v httpd) &>/dev/null;;
    esac
}

apache_reload() {

    info_msg "reload apache .."
    echo
    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            sudo -H apachectl configtest
            sudo -H systemctl force-reload apache2
            ;;
        arch-*| fedora-*)
            sudo -H httpd -t
            sudo -H systemctl force-reload httpd
            ;;
    esac
}

apache_install_site() {

    # usage:  apache_install_site [<template option> ...] <mysite.conf>
    #
    # <template option>:   see install_template

    local template_opts=()
    local pos_args=("$0")

    for i in "$@"; do
        case $i in
            -*) template_opts+=("$i");;
            *)  pos_args+=("$i");;
        esac
    done

    install_template "${template_opts[@]}" \
                     "${APACHE_SITES_AVAILABLE}/${pos_args[1]}" \
                     root root 644
    apache_enable_site "${pos_args[1]}"
    info_msg "installed apache site: ${pos_args[1]}"
}

apache_remove_site() {

    # usage:  apache_remove_site <mysite.conf>

    info_msg "remove apache site: $1"
    apache_dissable_site "$1"
    rm -f "${APACHE_SITES_AVAILABLE}/$1"
}

apache_enable_site() {

    # usage:  apache_enable_site <mysite.conf>

    local CONF="$1"

    info_msg "enable apache site: ${CONF}"

    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            sudo -H a2ensite -q "${CONF}"
            ;;
        arch-*)
            mkdir -p "${APACHE_SITES_ENABLED}"
            rm -f "${APACHE_SITES_ENABLED}/${CONF}"
            ln -s "${APACHE_SITES_AVAILABLE}/${CONF}" "${APACHE_SITES_ENABLED}/${CONF}"
            ;;
        fedora-*)
            mkdir -p "${APACHE_SITES_ENABLED}"
            rm -f "${APACHE_SITES_ENABLED}/${CONF}"
            ln -s "${APACHE_SITES_AVAILABLE}/${CONF}" "${APACHE_SITES_ENABLED}/${CONF}"
            ;;
    esac
    apache_reload
}

apache_dissable_site() {

    # usage:  apache_disable_site <mysite.conf>

    local CONF="$1"

    info_msg "disable apache site: ${CONF}"

    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            sudo -H a2dissite -q "${CONF}"
            ;;
        arch-*)
            rm -f "${APACHE_SITES_ENABLED}/${CONF}"
            ;;
        fedora-*)
            rm -f "${APACHE_SITES_ENABLED}/${CONF}"
            ;;
    esac
    apache_reload
}

# uWSGI
# -----

uWSGI_SETUP="${uWSGI_SETUP:=/etc/uwsgi}"
uWSGI_USER=
uWSGI_GROUP=

# How distros manage uWSGI apps is very different.  From uWSGI POV read:
# - https://uwsgi-docs.readthedocs.io/en/latest/Management.html

uWSGI_distro_setup() {
    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            # init.d --> /usr/share/doc/uwsgi/README.Debian.gz
            # For uWSGI debian uses the LSB init process, this might be changed
            # one day, see https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=833067
            uWSGI_APPS_AVAILABLE="${uWSGI_SETUP}/apps-available"
            uWSGI_APPS_ENABLED="${uWSGI_SETUP}/apps-enabled"
            uWSGI_PACKAGES="uwsgi"
            ;;
        arch-*)
            # systemd --> /usr/lib/systemd/system/uwsgi@.service
            # For uWSGI archlinux uses systemd template units, see
            # - http://0pointer.de/blog/projects/instances.html
            # - https://uwsgi-docs.readthedocs.io/en/latest/Systemd.html#one-service-per-app-in-systemd
            uWSGI_APPS_AVAILABLE="${uWSGI_SETUP}/apps-archlinux"
            uWSGI_APPS_ENABLED="${uWSGI_SETUP}"
            uWSGI_PACKAGES="uwsgi"
            ;;
        fedora-*)
            # systemd --> /usr/lib/systemd/system/uwsgi.service
            # The unit file starts uWSGI in emperor mode (/etc/uwsgi.ini), see
            # - https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html
            uWSGI_APPS_AVAILABLE="${uWSGI_SETUP}/apps-available"
            uWSGI_APPS_ENABLED="${uWSGI_SETUP}.d"
            uWSGI_PACKAGES="uwsgi"
            uWSGI_USER="uwsgi"
            uWSGI_GROUP="uwsgi"
            ;;
        *)
            err_msg "$DIST_ID-$DIST_VERS: uWSGI not yet implemented"
            ;;
esac
}

uWSGI_distro_setup

install_uwsgi(){
    info_msg "installing uwsgi ..."
    pkg_install "$uWSGI_PACKAGES"
    case $DIST_ID-$DIST_VERS in
        fedora-*)
            # enable & start should be called once at uWSGI installation time
            systemctl enable uwsgi
            systemctl restart uwsgi
            ;;
    esac
}

uWSGI_restart() {

    # usage:  uWSGI_restart() <myapp.ini>

    local CONF="$1"

    [[ -z $CONF ]] && die_caller 42 "missing argument <myapp.ini>"
    info_msg "restart uWSGI service"
    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            # the 'service' method seems broken in that way, that it (re-)starts
            # the whole uwsgi process.
            service uwsgi restart "${CONF%.*}"
            ;;
        arch-*)
            # restart systemd template instance
            if uWSGI_app_available "${CONF}"; then
                systemctl restart "uwsgi@${CONF%.*}"
            else
                info_msg "[uWSGI:systemd-template] ${CONF} not installed (no need to restart)"
            fi
            ;;
        fedora-*)
            # in emperor mode, just touch the file to restart
            if uWSGI_app_enabled "${CONF}"; then
                touch "${uWSGI_APPS_ENABLED}/${CONF}"
                # it seems, there is a polling time in between touch and restart
                # of the service.
                sleep 3
            else
                info_msg "[uWSGI:emperor] ${CONF} not installed (no need to restart)"
            fi
            ;;
        *)
            err_msg "$DIST_ID-$DIST_VERS: uWSGI not yet implemented"
            return 42
            ;;
    esac
}

uWSGI_prepare_app() {

    # usage:  uWSGI_prepare_app <myapp.ini>

    [[ -z $1 ]] && die_caller 42 "missing argument <myapp.ini>"

    local APP="${1%.*}"

    case $DIST_ID-$DIST_VERS in
        fedora-*)
            # in emperor mode, the uwsgi user is the owner of the sockets
            info_msg "prepare (uwsgi:uwsgi)  /run/uwsgi/app/${APP}"
            mkdir -p "/run/uwsgi/app/${APP}"
            chown -R "uwsgi:uwsgi"  "/run/uwsgi/app/${APP}"
            ;;
        *)
            info_msg "prepare (${SERVICE_USER}:${SERVICE_GROUP})  /run/uwsgi/app/${APP}"
            mkdir -p "/run/uwsgi/app/${APP}"
            chown -R "${SERVICE_USER}:${SERVICE_GROUP}"  "/run/uwsgi/app/${APP}"
            ;;
    esac
}


uWSGI_app_available() {
    # usage:  uWSGI_app_available <myapp.ini>
    local CONF="$1"

    [[ -z $CONF ]] && die_caller 42 "missing argument <myapp.ini>"
    [[ -f "${uWSGI_APPS_AVAILABLE}/${CONF}" ]]
}

uWSGI_install_app() {

    # usage:  uWSGI_install_app [<template option> ...] <myapp.ini>
    #
    # <template option>:  see install_template

    local pos_args=("$0")

    for i in "$@"; do
        case $i in
            -*) template_opts+=("$i");;
            *)  pos_args+=("$i");;
        esac
    done
    uWSGI_prepare_app "${pos_args[1]}"
    mkdir -p "${uWSGI_APPS_AVAILABLE}"
    install_template "${template_opts[@]}" \
                     "${uWSGI_APPS_AVAILABLE}/${pos_args[1]}" \
                     root root 644
    uWSGI_enable_app "${pos_args[1]}"
    uWSGI_restart "${pos_args[1]}"
    info_msg "uWSGI app: ${pos_args[1]} is installed"
}

uWSGI_remove_app() {

    # usage:  uWSGI_remove_app <myapp.ini>

    local CONF="$1"

    [[ -z $CONF ]] && die_caller 42 "missing argument <myapp.ini>"
    info_msg "remove uWSGI app: ${CONF}"
    uWSGI_disable_app "${CONF}"
    uWSGI_restart "${CONF}"
    rm -f "${uWSGI_APPS_AVAILABLE}/${CONF}"
}

uWSGI_app_enabled() {
    # usage:  uWSGI_app_enabled <myapp.ini>

    local exit_val=0
    local CONF="$1"

    [[ -z $CONF ]] && die_caller 42 "missing argument <myapp.ini>"
    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            [[ -f "${uWSGI_APPS_ENABLED}/${CONF}" ]]
            exit_val=$?
            ;;
        arch-*)
            systemctl -q is-enabled "uwsgi@${CONF%.*}"
            exit_val=$?
            ;;
        fedora-*)
            [[ -f "${uWSGI_APPS_ENABLED}/${CONF}" ]]
            exit_val=$?
            ;;
        *)
            # FIXME
            err_msg "$DIST_ID-$DIST_VERS: uWSGI not yet implemented"
            exit_val=1
            ;;
    esac
    return $exit_val
}

# shellcheck disable=SC2164
uWSGI_enable_app() {

    # usage:   uWSGI_enable_app <myapp.ini>

    local CONF="$1"

    [[ -z $CONF ]] && die_caller 42 "missing argument <myapp.ini>"
    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            mkdir -p "${uWSGI_APPS_ENABLED}"
            rm -f "${uWSGI_APPS_ENABLED}/${CONF}"
            ln -s "${uWSGI_APPS_AVAILABLE}/${CONF}" "${uWSGI_APPS_ENABLED}/${CONF}"
            info_msg "enabled uWSGI app: ${CONF} (restart required)"
            ;;
        arch-*)
            mkdir -p "${uWSGI_APPS_ENABLED}"
            rm -f "${uWSGI_APPS_ENABLED}/${CONF}"
            ln -s "${uWSGI_APPS_AVAILABLE}/${CONF}" "${uWSGI_APPS_ENABLED}/${CONF}"
            systemctl enable "uwsgi@${CONF%.*}"
            info_msg "enabled uWSGI app: ${CONF} (restart required)"
            ;;
        fedora-*)
            mkdir -p "${uWSGI_APPS_ENABLED}"
            rm -f "${uWSGI_APPS_ENABLED}/${CONF}"
            ln -s "${uWSGI_APPS_AVAILABLE}/${CONF}" "${uWSGI_APPS_ENABLED}/${CONF}"
            chown "${uWSGI_USER}:${uWSGI_GROUP}" "${uWSGI_APPS_ENABLED}/${CONF}"
            info_msg "enabled uWSGI app: ${CONF}"
            ;;
        *)
            # FIXME
            err_msg "$DIST_ID-$DIST_VERS: uWSGI not yet implemented"
            ;;
    esac
}

uWSGI_disable_app() {

    # usage:   uWSGI_disable_app <myapp.ini>

    local CONF="$1"

    [[ -z $CONF ]] && die_caller 42 "missing argument <myapp.ini>"
    case $DIST_ID-$DIST_VERS in
        ubuntu-*|debian-*)
            service uwsgi stop "${CONF%.*}"
            rm -f "${uWSGI_APPS_ENABLED}/${CONF}"
            info_msg "disabled uWSGI app: ${CONF} (restart uWSGI required)"
            ;;
        arch-*)
            systemctl stop "uwsgi@${CONF%.*}"
            systemctl disable "uwsgi@${CONF%.*}"
            rm -f "${uWSGI_APPS_ENABLED}/${CONF}"
            ;;
        fedora-*)
            # in emperor mode, just remove the app.ini file
            rm -f "${uWSGI_APPS_ENABLED}/${CONF}"
            ;;
        *)
            # FIXME
            err_msg "$DIST_ID-$DIST_VERS: uWSGI not yet implemented"
            ;;
    esac
}

# distro's package manager
# ------------------------

_apt_pkg_info_is_updated=0

pkg_install() {

    # usage: TITEL='install foobar' pkg_install foopkg barpkg

    rst_title "${TITLE:-installation of packages}" section
    echo -e "\npackage(s)::\n"
    # shellcheck disable=SC2068
    echo "  " $@ | $FMT

    if ! ask_yn "Should packages be installed?" Yn 30; then
        return 42
    fi
    case $DIST_ID in
        ubuntu|debian)
            if [[ $_apt_pkg_info_is_updated == 0 ]]; then
                export _apt_pkg_info_is_updated=1
                apt update
            fi
            # shellcheck disable=SC2068
            apt-get install -m -y $@
            ;;
        arch)
            # shellcheck disable=SC2068
            pacman -Sy --noconfirm $@
            ;;
        fedora)
            # shellcheck disable=SC2068
            dnf install -y $@
            ;;
    esac
}

pkg_remove() {

    # usage: TITEL='remove foobar' pkg_remove foopkg barpkg

    rst_title "${TITLE:-remove packages}" section
    echo -e "\npackage(s)::\n"
    # shellcheck disable=SC2068
    echo "  " $@ | $FMT

    if ! ask_yn "Should packages be removed (purge)?" Yn 30; then
        return 42
    fi
    case $DIST_ID in
        ubuntu|debian)
            # shellcheck disable=SC2068
            apt-get purge --autoremove --ignore-missing -y $@
            ;;
        arch)
            # shellcheck disable=SC2068
            pacman -R --noconfirm $@
            ;;
        fedora)
            # shellcheck disable=SC2068
            dnf remove -y $@
            ;;
    esac
}

pkg_is_installed() {

    # usage: pkg_is_install foopkg || pkg_install foopkg

    case $DIST_ID in
        ubuntu|debian)
            dpkg -l "$1" &> /dev/null
            return $?
            ;;
        arch)
            pacman -Qsq "$1" &> /dev/null
            return $?
            ;;
        fedora)
            dnf list -q --installed "$1" &> /dev/null
            return $?
            ;;
    esac
}

# git tooling
# -----------

# shellcheck disable=SC2164
git_clone() {

    # usage:
    #
    #    git_clone <url> <name> [<branch> [<user>]]
    #    git_clone <url> <path> [<branch> [<user>]]
    #
    #  First form uses $CACHE/<name> as destination folder, second form clones
    #  into <path>.  If repository is allready cloned, pull from <branch> and
    #  update working tree (if needed, the caller has to stash local changes).
    #
    #    git clone https://github.com/asciimoo/searx searx-src origin/master searxlogin
    #

    local url="$1"
    local dest="$2"
    local branch="$3"
    local user="$4"
    local bash_cmd="bash"
    local remote="origin"

    if [[ ! "${dest:0:1}" = "/" ]]; then
        dest="$CACHE/$dest"
    fi

    [[ -z $branch ]] && branch=master
    [[ -z $user ]] && [[ -n "${SUDO_USER}" ]] && user="${SUDO_USER}"
    [[ -n $user ]] && bash_cmd="sudo -H -u $user -i"

    if [[ -d "${dest}" ]] ; then
        info_msg "already cloned: $dest"
        tee_stderr 0.1 <<EOF | $bash_cmd 2>&1 |  prefix_stdout "  ${_Yellow}|$user|${_creset} "
cd "${dest}"
git checkout -m -B "$branch" --track "$remote/$branch"
git pull --all
EOF
    else
        info_msg "clone into: $dest"
        tee_stderr 0.1 <<EOF | $bash_cmd 2>&1 |  prefix_stdout "  ${_Yellow}|$user|${_creset} "
mkdir -p "$(dirname "$dest")"
cd "$(dirname "$dest")"
git clone --branch "$branch" --origin "$remote" "$url" "$(basename "$dest")"
EOF
    fi
}

# containers
# ----------

in_container() {
    # Test if shell runs in a container.
    #
    # usage:  in_container && echo "process running inside a LXC container"
    #         in_container || echo "process is not running inside a LXC container"
    #
    # sudo_or_exit
    # hint:   Reads init process environment, therefore root access is required!
    # to be safe, take a look at the environment of process 1 (/sbin/init)
    # grep -qa 'container=lxc' /proc/1/environ

    # see lxc_init_container_env
    [[ -f /.lxcenv ]]
}

LXC_ENV_FOLDER=
if in_container; then
    # shellcheck disable=SC2034
    LXC_ENV_FOLDER="lxc/$(hostname)/"
fi

lxc_init_container_env() {

    # usage: lxc_init_container_env <name>

    # Create a /.lxcenv file in the root folder.  Call this once after the
    # container is inital started and before installing any boilerplate stuff.

    info_msg "create /.lxcenv in container $1"
    cat <<EOF | lxc exec "${1}" -- bash | prefix_stdout "[${_BBlue}${1}${_creset}] "
touch "/.lxcenv"
ls -l "/.lxcenv"
EOF
}

# apt packages
LXC_BASE_PACKAGES_debian="bash git build-essential python3 virtualenv"

# pacman packages
LXC_BASE_PACKAGES_arch="bash git base-devel python python-virtualenv"

# dnf packages
LXC_BASE_PACKAGES_fedora="bash git @development-tools python virtualenv"

case $DIST_ID in
    ubuntu|debian) LXC_BASE_PACKAGES="${LXC_BASE_PACKAGES_debian}" ;;
    arch)          LXC_BASE_PACKAGES="${LXC_BASE_PACKAGES_arch}" ;;
    fedora)        LXC_BASE_PACKAGES="${LXC_BASE_PACKAGES_fedora}" ;;
    *) err_msg "$DIST_ID-$DIST_VERS: pkg_install LXC_BASE_PACKAGES not yet implemented" ;;
esac

lxc_install_base_packages() {
    info_msg "install LXC_BASE_PACKAGES in container $1"
    pkg_install "${LXC_BASE_PACKAGES}"
}


lxc_image_copy() {

    # usage: lxc_copy_image <remote image> <local image>
    #
    #        lxc_copy_image "images:ubuntu/19.10"  "ubu1910"

    if lxc_image_exists "local:${LXC_SUITE[i+1]}"; then
        info_msg "image ${LXC_SUITE[i]} already copied --> ${LXC_SUITE[i+1]}"
    else
        info_msg "copy image locally ${LXC_SUITE[i]} --> ${LXC_SUITE[i+1]}"
        lxc image copy "${LXC_SUITE[i]}" local: \
            --alias  "${LXC_SUITE[i+1]}" | prefix_stdout
    fi
}

lxc_init_container() {

    # usage: lxc_init_container <image name> <container name>

    local image_name="$1"
    local container_name="$2"

    if lxc info "${container_name}" &>/dev/null; then
        info_msg "container '${container_name}' already exists"
    else
        info_msg "create container instance: ${container_name}"
        lxc init "local:${image_name}" "${container_name}"
    fi
}

lxc_exists(){

    # usage: lxc_exists <name> || echo "container <name> does not exists"

    lxc info "$1" &>/dev/null
}

lxc_image_exists(){
    # usage: lxc_image_exists <alias> || echo "image <alias> does locally not exists"

    lxc image info "local:$1" &>/dev/null

}

lxc_delete_container() {

    #  usage: lxc_delete_container <container-name>

    if lxc info "$1" &>/dev/null; then
        info_msg "stop & delete instance ${_BBlue}${1}${_creset}"
        lxc stop "$1" &>/dev/null
        lxc delete "$1" | prefix_stdout
    else
        warn_msg "instance '$1' does not exist / can't delete :o"
    fi
}

lxc_delete_local_image() {

    #  usage: lxc_delete_local_image <container-name>

    info_msg "delete image 'local:$i'"
    lxc image delete "local:$i"
}


# IP
# --

global_IPs(){
    # usage: global_IPS
    #
    # print list of host's SCOPE global addresses and adapters e.g::
    #
    #   $ global_IPs
    #   enp4s0|192.168.1.127
    #   lxdbr0|10.246.86.1
    #   lxdbr0|fd42:8c58:2cd:b73f::1

    ip -o addr show | sed -nr 's/[0-9]*:\s*([a-z0-9]*).*inet[6]?\s*([a-z0-9.:]*).*scope global.*/\1|\2/p'
}

primary_ip() {

    case $DIST_ID in
        arch)
            ip -o addr show \
                | sed -nr 's/[0-9]*:\s*([a-z0-9]*).*inet[6]?\s*([a-z0-9.:]*).*scope global.*/\2/p' \
                | head -n 1
            ;;
        *)  hostname -I | cut -d' ' -f1 ;;
    esac
}

# URL
# ---

url_replace_hostname(){

    # usage:  url_replace_hostname <url> <new hostname>

    # to replace hostname by primary IP::
    #
    #   url_replace_hostname http://searx-ubu1604/morty $(primary_ip)
    #   http://10.246.86.250/morty

    # shellcheck disable=SC2001
    echo "$1" | sed "s|\(http[s]*://\)[^/]*\(.*\)|\1$2\2|"
}
