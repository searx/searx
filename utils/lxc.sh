#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh indent-tabs-mode: nil -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

# shellcheck source=utils/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
source_dot_config

# load environment of the LXC suite
LXC_ENV="${LXC_ENV:-${REPO_ROOT}/utils/lxc-searx.env}"
source "$LXC_ENV"
lxc_set_suite_env

# ----------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------
#
# read also:
# - https://lxd.readthedocs.io/en/latest/

LXC_HOST_PREFIX="${LXC_HOST_PREFIX:-test}"

# where all folders from HOST are mounted
LXC_SHARE_FOLDER="/share"
LXC_REPO_ROOT="${LXC_SHARE_FOLDER}/$(basename "${REPO_ROOT}")"

ubu1604_boilerplate="
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y
apt-get install -y git curl wget
"
ubu1804_boilerplate="$ubu1604_boilerplate"
ubu1904_boilerplate="$ubu1804_boilerplate"
ubu1910_boilerplate="$ubu1904_boilerplate"

# shellcheck disable=SC2034
ubu2004_boilerplate="
$ubu1910_boilerplate
echo 'Set disable_coredump false' >> /etc/sudo.conf
"

# shellcheck disable=SC2034
archlinux_boilerplate="
pacman -Syu --noconfirm
pacman -S --noconfirm git curl wget sudo
echo 'Set disable_coredump false' >> /etc/sudo.conf
"

# shellcheck disable=SC2034
fedora31_boilerplate="
dnf update -y
dnf install -y git curl wget hostname
echo 'Set disable_coredump false' >> /etc/sudo.conf
"

REMOTE_IMAGES=()
CONTAINERS=()
LOCAL_IMAGES=()

for ((i=0; i<${#LXC_SUITE[@]}; i+=2)); do
    REMOTE_IMAGES=("${REMOTE_IMAGES[@]}" "${LXC_SUITE[i]}")
    CONTAINERS=("${CONTAINERS[@]}" "${LXC_HOST_PREFIX}-${LXC_SUITE[i+1]}")
    LOCAL_IMAGES=("${LOCAL_IMAGES[@]}" "${LXC_SUITE[i+1]}")
done

HOST_USER="${SUDO_USER:-$USER}"
HOST_USER_ID=$(id -u "${HOST_USER}")
HOST_GROUP_ID=$(id -g "${HOST_USER}")

# ----------------------------------------------------------------------------
usage() {
# ----------------------------------------------------------------------------
    _cmd="$(basename "$0")"
    cat <<EOF

usage::

  $_cmd build        [containers]
  $_cmd copy         [images]
  $_cmd remove       [containers|<name>|images|subordinate]
  $_cmd add          [subordinate]
  $_cmd [start|stop] [containers|<name>]
  $_cmd show         [info|config|suite|images]
  $_cmd cmd          [--|<name>] ...
  $_cmd install      [suite]

build
  :containers:   build & launch all LXC containers of the suite
copy:
  :images:       copy remote images of the suite into local storage
remove
  :containers:   delete all 'containers' or only <container-name>
  :images:       delete local images of the suite
add / remove
  :subordinate:  LXD permission to map ${HOST_USER}'s user/group id through
start/stop
  :containers:   start/stop all 'containers' from the suite
  :<name>:       start/stop conatiner <name> from suite
show
  :info:         show info of all the containers from LXC suite
  :config:       show config of all the containers from the LXC suite
  :suite:        show services of all the containers from the LXC suite
  :images:       show information of local images
cmd
  --             run command ... in all containers of the LXC suite
  :<name>:       run command ... in container <name>
install
  :suite:        install LXC suite, includes morty & filtron

Images of the LXC suite:
$(echo "  ${LOCAL_IMAGES[*]}" | $FMT)

Containers of the LXC suite:
$(echo "  ${CONTAINERS[*]}" | $FMT)
EOF
    [ -n "${1+x}" ] &&  err_msg "$1"
}

lxd_info() {

    cat <<EOF

LXD is needed, to install run::

  snap install lxd
  lxd init --auto

EOF
}

main() {

    local exit_val
    local _usage="unknown or missing $1 command $2"

    # don't check prerequisite when in recursion
    if [[ ! $1 == __* ]]; then
        ! required_commands lxc && lxd_info && exit 42
        [[ -z $LXC_SUITE ]] && err_msg "missing LXC_SUITE" && exit 42 
    fi

    case $1 in
        --source-only)  ;;
        -h|--help) usage; exit 0;;

        build)
            sudo_or_exit
            case $2 in
                ''|containers) build_instances ;;
                *) usage "$_usage"; exit 42;;
            esac
            ;;
        copy)
            case $2 in
                ''|images) lxc_copy_images_localy;;
                *) usage "$_usage"; exit 42;;
            esac
            ;;
        remove)
            sudo_or_exit
            case $2 in
                ''|containers) remove_instances ;;
                images) lxc_delete_images_localy ;;
                subordinate) echo; del_subordinate_ids ;;
                ${LXC_HOST_PREFIX}-*)
                    if ask_yn "Do you really want to delete conatiner $2"; then
                        lxc_delete_container "$2"
                    fi
                    ;;
                *) usage "unknown (or mising) container <name> $2"; exit 42;;
            esac
            ;;
        add)
            sudo_or_exit
            case $2 in
                subordinate) echo; add_subordinate_ids ;;
                *) usage "$_usage"; exit 42;;
            esac
            ;;
        start|stop)
            sudo_or_exit
            case $2 in
                ''|containers)  lxc_cmd "$1" ;;
                ${LXC_HOST_PREFIX}-*)
                    info_msg "lxc $1 $2"
                    lxc "$1" "$2" | prefix_stdout "[${_BBlue}${i}${_creset}] "
                    ;;
                *) usage "ukknown or missing container <name> $2"; exit 42;;
            esac
            ;;
        show)
            sudo_or_exit
            case $2 in
                suite)  show_suite ;;
                images) show_images ;;
                config)
                    rst_title "container configurations"
                    echo
                    lxc list "$LXC_HOST_PREFIX-"
                    echo
                    lxc_cmd config show
                    ;;
                info)
                    rst_title "container info"
                    echo
                    lxc_cmd info
                    ;;
                *) usage "$_usage"; exit 42;;
            esac
            ;;
        __show)
            case $2 in
                suite) lxc_suite_info ;;
            esac
            ;;
        cmd)
            sudo_or_exit
            shift
            case $1 in
                --)
                    shift
                    for name in "${CONTAINERS[@]}"; do
                        lxc_exec_cmd "${name}" "$@"
                    done
                    ;;
                ${LXC_HOST_PREFIX}-*)
                    local name=$1
                    shift
                    lxc_exec_cmd "${name}" "$@"
                    ;;

                *) usage "unknown <name>: $1"; exit 42
                   ;;
            esac
            ;;
        install)
            sudo_or_exit
            case $2 in
                suite) install_suite ;;
                *) usage "$_usage"; exit 42 ;;
            esac
            ;;
        __install)
            case $2 in
                suite) lxc_suite_install ;;
            esac
            ;;
        doc)
            echo
            echo ".. generic utils/lxc.sh documentation"
            ;;
        -*) usage "unknown option $1"; exit 42;;
        *)  usage "unknown or missing command $1"; exit 42;;
    esac
}


build_instances() {
    rst_title "Build LXC instances"
    echo
    add_subordinate_ids
    lxc_copy_images_localy
    echo
    rst_title "build containers" section
    echo
    lxc_init_containers
    lxc_config_containers
    lxc_boilerplate_containers
    echo
    lxc list "$LXC_HOST_PREFIX"
}

remove_instances() {
    rst_title "Remove LXC instances"
    rst_para "existing containers matching ${_BGreen}$LXC_HOST_PREFIX-*${_creset}"
    echo
    lxc list "$LXC_HOST_PREFIX-"
    echo -en "\\n${_BRed}LXC containers to delete::${_creset}\\n\\n  ${CONTAINERS[*]}\\n" | $FMT
    if ask_yn "Do you really want to delete these conatiners"; then
        for i in "${CONTAINERS[@]}"; do
            lxc_delete_container "$i"
        done
    fi
    echo
    lxc list "$LXC_HOST_PREFIX-"
}

# images
# ------

lxc_copy_images_localy() {
    rst_title "copy images" section
    echo
    for ((i=0; i<${#LXC_SUITE[@]}; i+=2)); do
        if lxc_image_exists "local:${LXC_SUITE[i+1]}"; then
            info_msg "image ${LXC_SUITE[i]} already copied --> ${LXC_SUITE[i+1]}"
        else
            info_msg "copy image locally ${LXC_SUITE[i]} --> ${LXC_SUITE[i+1]}"
            lxc image copy "${LXC_SUITE[i]}" local: \
                --alias  "${LXC_SUITE[i+1]}" | prefix_stdout
        fi
    done
    # lxc image list local: && wait_key
}

lxc_delete_images_localy() {
    rst_title "Delete LXC images"
    rst_para "local existing images"
    echo
    lxc image list local:
    echo -en "\\n${_BRed}LXC images to delete::${_creset}\\n\\n  ${LOCAL_IMAGES[*]}\\n"
    if ask_yn "Do you really want to delete these images"; then
        for i in "${LOCAL_IMAGES[@]}"; do
            lxc_delete_local_image "$i"
        done
    fi
    echo
    lxc image list local:
}

show_images(){
    rst_title "local images"
    echo
    lxc image list local:
    echo -en "\\n${_Green}LXC suite images::${_creset}\\n\\n  ${LOCAL_IMAGES[*]}\\n"
    wait_key
    for i in "${LOCAL_IMAGES[@]}"; do
        if lxc_image_exists "$i"; then
            info_msg "lxc image info ${_BBlue}${i}${_creset}"
            lxc image info "$i" | prefix_stdout "[${_BBlue}${i}${_creset}] "
        else
            warn_msg "image ${_BBlue}$i${_creset} does not yet exists"
        fi
    done

}


# container
# ---------

show_suite(){
    rst_title "LXC suite ($LXC_HOST_PREFIX-*)"
    echo
    lxc list "$LXC_HOST_PREFIX-"
    echo
    for i in "${CONTAINERS[@]}"; do
        if ! lxc_exists "$i"; then
            warn_msg "container ${_BBlue}$i${_creset} does not yet exists"
        else
            lxc exec -t "${i}" -- "${LXC_REPO_ROOT}/utils/lxc.sh" __show suite \
                | prefix_stdout "[${_BBlue}${i}${_creset}]  "
        fi
    done
}

install_suite() {
    for i in "${CONTAINERS[@]}"; do
        if ! lxc_exists "$i"; then
            warn_msg "container ${_BBlue}$i${_creset} does not yet exists"
        else
            info_msg "[${_BBlue}${i}${_creset}] ${_BGreen}${LXC_REPO_ROOT}/utils/lxc.sh install suite${_creset}"
            lxc exec -t "${i}" -- "${LXC_REPO_ROOT}/utils/lxc.sh" __install suite \
                | prefix_stdout "[${_BBlue}${i}${_creset}]  "
        fi
    done
}

lxc_cmd() {
    for i in "${CONTAINERS[@]}"; do
        if ! lxc_exists "$i"; then
            warn_msg "container ${_BBlue}$i${_creset} does not yet exists"
        else
            info_msg "lxc $* $i"
            lxc "$@" "$i" | prefix_stdout "[${_BBlue}${i}${_creset}] "
            echo
        fi
    done
}

lxc_exec_cmd() {
    local name="$1"
    shift
    exit_val=
    info_msg "[${_BBlue}${name}${_creset}] ${_BGreen}${*}${_creset}"
    lxc exec "${name}" -- "$@"
    exit_val=$?
    if [[ $exit_val -ne 0 ]]; then
        warn_msg "[${_BBlue}${i}${_creset}] exit code (${_BRed}${exit_val}${_creset}) from ${_BGreen}${*}${_creset}"
    else
        info_msg "[${_BBlue}${i}${_creset}] exit code (${exit_val}) from ${_BGreen}${*}${_creset}"
    fi
    echo
}

lxc_init_containers() {

    local image_name
    local container_name

    for ((i=0; i<${#LXC_SUITE[@]}; i+=2)); do

        image_name="${LXC_SUITE[i+1]}"
        container_name="${LXC_HOST_PREFIX}-${image_name}"

        if lxc info "${container_name}" &>/dev/null; then
            info_msg "container '${container_name}' already exists"
        else
            info_msg "create conatiner instance: ${container_name}"
            lxc init "local:${image_name}" "${container_name}"
        fi
    done
}

lxc_config_containers() {
    for i in "${CONTAINERS[@]}"; do
        info_msg "[${_BBlue}${i}${_creset}] configure container ..."

        info_msg "[${_BBlue}${i}${_creset}] map uid/gid from host to container"
        # https://lxd.readthedocs.io/en/latest/userns-idmap/#custom-idmaps
        echo -e -n "uid $HOST_USER_ID 1000\\ngid $HOST_GROUP_ID 1000"\
            | lxc config set "$i" raw.idmap -

        info_msg "[${_BBlue}${i}${_creset}] share ${REPO_ROOT} (repo_share) from HOST into container"
        # https://lxd.readthedocs.io/en/latest/instances/#type-disk
        lxc config device add "$i" repo_share disk \
            source="${REPO_ROOT}" \
            path="${LXC_REPO_ROOT}" &>/dev/null
        # lxc config show "$i" && wait_key
    done
}

lxc_boilerplate_containers() {

    local image_name
    local container_name
    local boilerplate_script

    for ((i=0; i<${#LXC_SUITE[@]}; i+=2)); do

        image_name="${LXC_SUITE[i+1]}"
        container_name="${LXC_HOST_PREFIX}-${image_name}"
        boilerplate_script="${image_name}_boilerplate"
        boilerplate_script="${!boilerplate_script}"

        info_msg "[${_BBlue}${container_name}${_creset}] install boilerplate"
        if lxc start -q "${container_name}" &>/dev/null; then
            sleep 5 # guest needs some time to come up and get an IP
        fi
        if [[ -n "${boilerplate_script}" ]]; then
            echo "${boilerplate_script}" \
                | lxc exec "${container_name}" -- bash \
                | prefix_stdout "[${_BBlue}${container_name}${_creset}] "
        else
            err_msg "[${_BBlue}${container_name}${_creset}] no boilerplate for image '${image_name}'"
        fi

    done
}

# subordinates
# ------------
#
# see man: subgid(5), subuid(5), https://lxd.readthedocs.io/en/latest/userns-idmap
#
# E.g. in the HOST you have uid=1001(user) and/or gid=1001(user) ::
#
#   root:1001:1
#
# in the CONTAINER::
#
#   config:
#     raw.idmap: |
#       uid 1001 1000
#       gid 1001 1000

add_subordinate_ids() {
    if  grep "root:${HOST_USER_ID}:1" /etc/subuid -qs; then
        info_msg "lxd already has permission to map ${HOST_USER_ID}'s user/group id through"
    else
        info_msg "add lxd permission to map ${HOST_USER_ID}'s user/group id through"
        usermod --add-subuids "${HOST_USER_ID}-${HOST_USER_ID}" \
                --add-subgids "${HOST_GROUP_ID}-${HOST_GROUP_ID}" root
    fi
}

del_subordinate_ids() {
    local out
    local exit_val
    if  grep "root:${HOST_USER_ID}:1" /etc/subuid -qs; then
        # TODO: root user is always in use by process 1, how can we remove subordinates?
        info_msg "remove lxd permission to map ${HOST_USER_ID}'s user/group id through"
        out=$(usermod --del-subuids "${HOST_USER_ID}-${HOST_USER_ID}" --del-subgids "${HOST_GROUP_ID}-${HOST_GROUP_ID}" root 2>&1)
        exit_val=$?
        if [ $exit_val -ne 0 ]; then
            err_msg "$out"
        fi
    else
        info_msg "lxd does not have permission to map ${HOST_USER_ID}'s user/group id through"
    fi
}


# ----------------------------------------------------------------------------
main "$@"
# ----------------------------------------------------------------------------