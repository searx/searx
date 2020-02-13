#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh indent-tabs-mode: nil -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

# shellcheck source=utils/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
source_dot_config

# ----------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------
#
# read also:
# - https://lxd.readthedocs.io/en/latest/

# name of https://images.linuxcontainers.org
LINUXCONTAINERS_ORG_NAME="${LINUXCONTAINERS_ORG_NAME:-images}"
HOST_PREFIX="${HOST_PREFIX:-searx}"

TEST_IMAGES=(
    "$LINUXCONTAINERS_ORG_NAME:ubuntu/18.04"  "ubu1804"
    "$LINUXCONTAINERS_ORG_NAME:ubuntu/19.04"  "ubu1904"

    # TODO: installation of searx & filtron not yet implemented ..
    #
    #"$LINUXCONTAINERS_ORG_NAME:archlinux"     "archlinux"
    #"$LINUXCONTAINERS_ORG_NAME:fedora/31"     "fedora31"
)

REMOTE_IMAGES=()
LOCAL_IMAGES=()

for ((i=0; i<${#TEST_IMAGES[@]}; i+=2)); do
    REMOTE_IMAGES=("${REMOTE_IMAGES[@]}" "${TEST_IMAGES[i]}")
    LOCAL_IMAGES=("${LOCAL_IMAGES[@]}" "${TEST_IMAGES[i+1]}")
done

HOST_USER="${SUDO_USER:-$USER}"
HOST_USER_ID=$(id -u "${HOST_USER}")
HOST_GROUP_ID=$(id -g "${HOST_USER}")

# ----------------------------------------------------------------------------
usage() {
# ----------------------------------------------------------------------------

    cat <<EOF

usage::

  $(basename "$0") build        [containers]
  $(basename "$0") delete       [containers|subordinate]
  $(basename "$0") [start|stop] [containers]
  $(basename "$0") inspect      [info|config]
  $(basename "$0") cmd          ...

build / delete
  :containers:   build and delete all LXC containers
add / delete
  :subordinate:  lxd permission to map ${HOST_USER}'s user/group id through
start/stop
  :containers:   start/stop of all containers
inspect
  :info:    show info of all containers
  :config:  show config of all containers
cmd ...
  run commandline ... in all containers

all LXC containers:
  ${LOCAL_IMAGES[@]}

EOF
    [ ! -z "${1+x}" ] &&  err_msg "$1"
}

main() {

    required_commands lxc || exit

    local _usage="unknown or missing $1 command $2"

    case $1 in
        --source-only)  ;;
        -h|--help) usage; exit 0;;

        build)
            sudo_or_exit
            case $2 in
                containers) build_instances ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        delete)
            sudo_or_exit
            case $2 in
                containers) delete_instances ;;
                subordinate) echo; del_subordinate_ids ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        add)
            sudo_or_exit
            case $2 in
                subordinate) echo; add_subordinate_ids ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        start|stop)
            sudo_or_exit
            case $2 in
                containers)  lxc_cmd "$1" ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        inspect)
            sudo_or_exit
            case $2 in
                config) lxc_cmd config show;;
                info) lxc_cmd info;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        cmd)
            sudo_or_exit
            shift
            for i in "${LOCAL_IMAGES[@]}"; do
                info_msg "lxc exec ${_BBlue}${HOST_PREFIX}-${i}${_creset} -- ${_BGreen}${*}${_creset}"
                lxc exec "${HOST_PREFIX}-${i}" -- "$@"
            done
            ;;
        *)
            usage "unknown or missing command $1"; exit 42;;
    esac
}

build_instances() {
    rst_title "Build LXC instances"
    lxc_copy_images_localy
    #lxc image list local: && wait_key
    lxc_init_containers
    lxc_config_containers
    lxc list "$HOST_PREFIX"
}

delete_instances() {
    rst_title "Delete LXC instances"
    echo -en "\\nLXC containers(s)::\\n\\n  ${LOCAL_IMAGES[*]}\\n" | $FMT
    if ask_yn "Do you really want to delete all images"; then
        lxc_delete_containers
    fi
    # lxc list "$HOST_PREFIX"
    # lxc image list local: && wait_key
}

# images
# ------

lxc_copy_images_localy() {
    echo
    for ((i=0; i<${#TEST_IMAGES[@]}; i+=2)); do
        if lxc image info "local:${TEST_IMAGES[i+1]}" &>/dev/null; then
            info_msg "image ${TEST_IMAGES[i]} already copied --> ${TEST_IMAGES[i+1]}"
        else
            info_msg "copy image locally ${TEST_IMAGES[i]} --> ${TEST_IMAGES[i+1]}"
            lxc image copy "${TEST_IMAGES[i]}" local: \
                --alias  "${TEST_IMAGES[i+1]}" prefix_stdout
        fi
    done
}

lxc_delete_images_localy() {
    echo
    for i in "${LOCAL_IMAGES[@]}"; do
        info_msg "delete image 'local:$i'"
        lxc image delete "local:$i"
    done
    #lxc image list local:
}

# container
# ---------

lxc_cmd() {
    echo
    for i in "${LOCAL_IMAGES[@]}"; do
        info_msg "lxc $* $HOST_PREFIX-$i"
        lxc "$@" "$HOST_PREFIX-$i"
    done
}

lxc_init_containers() {
    echo
    for i in "${LOCAL_IMAGES[@]}"; do
        if lxc info "$HOST_PREFIX-$i" &>/dev/null; then
            info_msg "conatiner '$HOST_PREFIX-$i' already exists"
        else
            info_msg "create conatiner instance: $HOST_PREFIX-$i"
            lxc init "local:$i" "$HOST_PREFIX-$i"
        fi
    done
}

lxc_config_containers() {
    echo
    for i in "${LOCAL_IMAGES[@]}"; do

        info_msg "map uid/gid from host to conatiner: $HOST_PREFIX-$i"
        # https://lxd.readthedocs.io/en/latest/userns-idmap/#custom-idmaps
        echo -e -n "uid $HOST_USER_ID 1000\\ngid $HOST_GROUP_ID 1000"\
            | lxc config set "$HOST_PREFIX-$i" raw.idmap -

        info_msg "share ${REPO_ROOT} (repo_share) from HOST into container: $HOST_PREFIX-$i"
        # https://lxd.readthedocs.io/en/latest/instances/#type-disk
        lxc config device add "$HOST_PREFIX-$i" repo_share disk \
            source="${REPO_ROOT}" \
            path="/share/$(basename "${REPO_ROOT}")"

        # lxc config show "$HOST_PREFIX-$i" && wait_key
    done
}

lxc_delete_containers() {
    echo
    for i in "${LOCAL_IMAGES[@]}"; do
        if lxc info "$HOST_PREFIX-$i" &>/dev/null; then
            info_msg "stop & delete instance '$HOST_PREFIX-$i'"
            lxc stop "$HOST_PREFIX-$i" &>/dev/null
            lxc delete "$HOST_PREFIX-$i" | prefix_stdout
        else
            warn_msg "instance '$HOST_PREFIX-$i' does not exist / can't delete :o"
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
    if  grep "root:${HOST_USER_ID}:1" /etc/subuid -qs; then
        # TODO: root user is always in use by process 1, how can we remove subordinates?
        info_msg "remove lxd permission to map ${HOST_USER_ID}'s user/group id through"
        out=$(usermod --del-subuids "${HOST_USER_ID}-${HOST_USER_ID}" --del-subgids "${HOST_GROUP_ID}-${HOST_GROUP_ID}" root 2>&1)
        if [ ! -z $? ]; then
            err_msg "$out"
        fi
    else
        info_msg "lxd does not have permission to map ${HOST_USER_ID}'s user/group id through"
    fi
}


# ----------------------------------------------------------------------------
main "$@"
# ----------------------------------------------------------------------------
