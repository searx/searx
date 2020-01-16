#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh indent-tabs-mode: nil -*-
# shellcheck disable=SC2059,SC1117,SC2162,SC2004

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

if [[ -z "$SYSTEMD_UNITS" ]]; then
    SYSTEMD_UNITS="/lib/systemd/system"
fi

if [[ -z ${DIFF_CMD} ]]; then
    DIFF_CMD="diff -u"
    if command -v colordiff >/dev/null;  then
        DIFF_CMD="colordiff -u"
    fi
fi

sudo_or_exit() {
    # usage: sudo_or_exit

    if [ ! "$(id -u)" -eq 0 ];  then
        err_msg "this command requires root (sudo) privilege!" >&2
        exit 42
    fi
}

rst_title() {
    # usage: rst_title <header-text> [part|chapter|section]

    case ${2-chapter} in
        part)     printf "\n${1//?/=}\n$1\n${1//?/=}\n";;
        chapter)  printf "\n${1}\n${1//?/=}\n";;
        section)  printf "\n${1}\n${1//?/-}\n";;
        *)
            err_msg "invalid argument '${2}' in line $(caller)"
            return 42
            ;;
    esac
}

if command -v fmt >/dev/null; then
    export FMT="fmt -u"
else
    export FMT="cat"
fi

rst_para() {
    # usage:  RST_INDENT=1 rst_para "lorem ipsum ..."
    local prefix=''
    if ! [[ -z $RST_INDENT ]] && [[ $RST_INDENT -gt 0 ]]; then
        prefix="$(for i in $(seq 1 "$RST_INDENT"); do printf "  "; done)"
        echo -en "\n$*\n" | $FMT | prefix_stdout "$prefix"
    else
        echo -en "\n$*\n" | $FMT
    fi
}

err_msg()  { echo -e "ERROR: $*" >&2; }
warn_msg() { echo -e "WARN:  $*" >&2; }
info_msg() { echo -e "INFO:  $*"; }

clean_stdin() {
    if [[ $(uname -s) != 'Darwin' ]]; then
        while read -n1 -t 0.1; do : ; done
    fi
}

wait_key(){
    # usage: waitKEY [<timeout in sec>]

    clean_stdin
    local _t=$1
    [[ ! -z $FORCE_TIMEOUT ]] && _t=$FORCE_TIMEOUT
    [[ ! -z $_t ]] && _t="-t $_t"
    # shellcheck disable=SC2086
    read -s -n1 $_t -p "** press any [KEY] to continue **"
    echo
    clean_stdin
}

ask_yn() {
    # usage: ask_yn <prompt-text> [Ny|Yn] [<timeout in sec>]

    local EXIT_YES=0 # exit status 0 --> successful
    local EXIT_NO=1  # exit status 1 --> error code

    local _t=$3
    [[ ! -z $FORCE_TIMEOUT ]] && _t=$FORCE_TIMEOUT
    [[ ! -z $_t ]] && _t="-t $_t"
    case "${2}" in
        Yn)
            local exit_val=${EXIT_YES}
            local choice="[YES/no]"
            local default="Yes"
            ;;
        *)
            local exit_val=${EXIT_NO}
            local choice="[NO/yes]"
            local default="No"
            ;;
    esac
    echo
    while true; do
        clean_stdin
        printf "$1 ${choice} "
        # shellcheck disable=SC2086
        read -n1 $_t
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
    if [[ ! -z $1 ]] ; then _t="$1"; fi

    (while read line; do
         # shellcheck disable=SC2086
         sleep $_t
         echo -e "$line" >&2
         echo "$line"
    done)
}

prefix_stdout () {
    # usage: <cmd> | prefix_stdout [prefix]

    local prefix="  | "

    if [[ ! -z $1 ]] ; then prefix="$1"; fi

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

    if [[ ! -z ${SUDO_USER} ]]; then
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
        if [[ ! -z ${SUDO_USER} ]]; then
            sudo -u "${SUDO_USER}" wget --progress=bar -O "${CACHE}/$2" "$1" ; exit_value=$?
        else
            wget --progress=bar -O "${CACHE}/$2" "$1" ; exit_value=$?
        fi
        if $exit_value; then
            err_msg "failed to download: $1"
        fi
    fi
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
    [[ ! -z $FORCE_TIMEOUT ]] && _t=$FORCE_TIMEOUT
    [[ ! -z $_t ]] && _t="-t $_t"

    list=("$@")
    echo -e "Menu::"
    for ((i=1; i<= $(($max -1)); i++)); do
        if [[ "$i" == "$default" ]]; then
            echo -e "  $i.) ${list[$i]} [default]"
        else
            echo -e "  $i.) ${list[$i]}"
        fi
    done
    while true; do
        clean_stdin
        printf "$1 [$default] "

        if (( 10 > $max )); then
            # shellcheck disable=SC2086
            read -n1 $_t
        else
            # shellcheck disable=SC2086,SC2229
            read $_t
        fi
        # selection fits
        [[ $REPLY =~ ^-?[0-9]+$ ]] && (( $REPLY > 0 )) && (( $REPLY < $max )) && break

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
    #     install_template [--no-eval] {file} [{owner} [{group} [{chmod}]]]
    #
    #     install_template --no-eval /etc/updatedb.conf root root 644

    local do_eval=1
    if [[ "$1" == "--no-eval" ]]; then
        do_eval=0; shift
    fi
    local dst="${1}"
    local owner=${2-$(id -un)}
    local group=${3-$(id -gn)}
    local chmod=${4-644}
    local _reply=""

    info_msg "install: ${dst}"

    if [[ ! -f "${TEMPLATES}${dst}" ]] ; then
        err_msg "${TEMPLATES}${dst} does not exists"
        err_msg "... can't install $dst / exit installation with error 42"
        wait_key 30
        return 42
    fi

    local template_file="${TEMPLATES}${dst}"
    if [[ "$do_eval" == "1" ]]; then
        info_msg "BUILD template ${template_file}"
        if [[ -f "${TEMPLATES}${dst}" ]] ; then
            template_file="${CACHE}${dst}"
            mkdir -p "$(dirname "${template_file}")"
            # shellcheck disable=SC2086
            eval "echo \"$(cat ${TEMPLATES}${dst})\"" > "${template_file}"
        else
            err_msg "failed ${template_file}"
            return 42
        fi
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

    info_msg "file ${dst} allready exists on this host"

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
                echo "// edit ${dst} to your needs"
                echo "// exit with CTRL-D"
                sudo -H -u "${owner}" -i
                $DIFF_CMD "${dst}" "${template_file}"
                if ask_yn "did you edit ${template_file} to your needs?"; then
                    break
                fi
                ;;
            "diff files")
                $DIFF_CMD "${dst}" "${template_file}" | prefix_stdout
        esac
    done
}


# uWSGI
# -----

uWSGI_SETUP="${uWSGI_SETUP:=/etc/uwsgi}"

uWSGI_restart() {

    # usage:  uWSGI_restart()

    info_msg "restart uWSGI service"
    sudo -H systemctl restart uwsgi
}

uWSGI_install_app() {

    # usage:  uWSGI_install_app [--no-eval] /etc/uwsgi/apps-available/myapp.ini

    local no_eval=""
    local CONF=""

    if [[ "$1" == "--no-eval" ]]; then
        no_eval=$1; shift
    fi

    CONF=$1
    # shellcheck disable=SC2086
    install_template $no_eval "${CONF}" root root 644
    uWSGI_enable_app "$(basename "${CONF}")"
    uWSGI_restart
    info_msg "installed uWSGI app: $(basename "${CONF}")"
}

uWSGI_remove_app() {

    # usage:  uWSGI_remove_app <path.ini>

    local CONF=$1
    uWSGI_disable_app "$(basename "${CONF}")"
    uWSGI_restart
    rm -f "$CONF"
    info_msg "removed uWSGI app: $(basename "${CONF}")"
}

# shellcheck disable=SC2164
uWSGI_enable_app() {

    # usage:   uWSGI_enable_app <path.ini>

    local CONF=$1
    if [[ -z $CONF ]]; then
        err_msg "uWSGI_enable_app missing arguments"
        return 42
    fi
    pushd "${uWSGI_SETUP}/apps-enabled" >/dev/null
    rm -f "$(basename "${CONF}")"
    # shellcheck disable=SC2226
    ln -s "../apps-available/$(basename "${CONF}")"
    info_msg "enabled uWSGI app: $(basename "${CONF}") (restart uWSGI required)"
    popd >/dev/null
}

uWSGI_disable_app() {

    # usage:   uWSGI_disable_app <path.ini>

    local CONF=$1
    if [[ -z $CONF ]]; then
        err_msg "uWSGI_enable_app missing arguments"
        return 42
    fi

    rm -f "${uWSGI_SETUP}/apps-enabled/$CONF"
    info_msg "disabled uWSGI app: $(basename "${CONF}") (restart uWSGI required)"
}

# distro's package manager
# ------------------------
#
# FIXME: Arch Linux & RHEL should be added
#

pkg_install() {

    # usage: TITEL='install foobar' pkg_install foopkg barpkg

    rst_title "${TITLE:-installation of packages}" section
    echo -en "\npackage(s)::\n\n  $*\n" | $FMT

    if ! ask_yn "Should packages be installed?" Yn 30; then
        return 42
    fi
    # shellcheck disable=SC2068
    apt-get install -y $@
}

pkg_remove() {

    # usage: TITEL='remove foobar' pkg_remove foopkg barpkg

    rst_title "${TITLE:-remove packages}" section
    echo -en "\npackage(s)::\n\n  $*\n" | $FMT

    if ! ask_yn "Should packages be removed (purge)?" Yn 30; then
        return 42
    fi
    apt-get purge --autoremove --ignore-missing -y "$@"
}

pkg_is_installed() {

    # usage: pkg_is_install foopkg || pkg_install foopkg

    dpkg -l "$1" &> /dev/null
    return $?
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
    [[ -z $user ]] && [[ ! -z "${SUDO_USER}" ]] && user="${SUDO_USER}"
    [[ ! -z $user ]] && bash_cmd="sudo -H -u $user -i"

    if [[ -d "${dest}" ]] ; then
        info_msg "already cloned: $dest"
	tee_stderr 0.1 <<EOF | $bash_cmd 2>&1 |  prefix_stdout "  |$user| "
cd "${dest}"
git checkout -m -B "$branch" --track "$remote/$branch"
git pull --all
EOF
    else
        info_msg "clone into: $dest"
	tee_stderr 0.1 <<EOF | $bash_cmd 2>&1 |  prefix_stdout "  |$user| "
mkdir -p "$(dirname "$dest")"
cd "$(dirname "$dest")"
git clone --branch "$branch" --origin "$remote" "$url" "$(basename "$dest")"
EOF
    fi
}
