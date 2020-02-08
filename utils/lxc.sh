#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh indent-tabs-mode: nil -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

# shellcheck source=utils/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
source_dot_config

# ----------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------

# name of https://images.linuxcontainers.org
LINUXCONTAINERS_ORG_NAME="${LINUXCONTAINERS_ORG_NAME:-images}"
HOST_PREFIX="${HOST_PREFIX:-searx}"

TEST_IMAGES=(
    "$LINUXCONTAINERS_ORG_NAME:ubuntu/18.04"  "ubu1804"
    "$LINUXCONTAINERS_ORG_NAME:ubuntu/19.04"  "ubu1904"
    "$LINUXCONTAINERS_ORG_NAME:archlinux"     "archlinux"
    #"$LINUXCONTAINERS_ORG_NAME:fedora/31"     "fedora31"
    #"ubuntu-minimal:18.04"  "ubu1804"
    #"ubuntu-minimal:19.10"  "ubu1910"
)

REMOTE_IMAGES=()
LOCAL_IMAGES=()

for ((i=0; i<${#TEST_IMAGES[@]}; i+=2)); do
    REMOTE_IMAGES=("${REMOTE_IMAGES[@]}" "${TEST_IMAGES[i]}")
    LOCAL_IMAGES=("${LOCAL_IMAGES[@]}" "${TEST_IMAGES[i+1]}")
done

# ----------------------------------------------------------------------------
usage() {
# ----------------------------------------------------------------------------

    cat <<EOF

usage::

  $(basename "$0") build [hosts]
  $(basename "$0") delete [hosts]

build / delete
  build and/or delete all LXC hosts

all LXC hosts:
  ${LOCAL_IMAGES[@]}

EOF
    [ ! -z "${1+x}" ] &&  err_msg "$1"
}

main() {
    rst_title "LXC tooling box" part

    required_commands lxc || exit

    local _usage="unknown or missing $1 command $2"

    case $1 in
        --source-only)  ;;
        -h|--help) usage; exit 0;;

        build)
            sudo_or_exit
            case $2 in
                hosts) build_instances ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        delete)
            sudo_or_exit
            case $2 in
                hosts) delete_instances ;;
                *) usage "$_usage"; exit 42;;
            esac ;;
        *)
            usage "unknown or missing command $1"; exit 42;;
    esac
}

build_instances() {
    rst_title "Build LXC instances"
    lxc_copy_images_localy
    lxc_init_containers

    err_msg "WIP / sorry, not implemented yet :o"
}

delete_instances() {
    rst_title "Delete LXC instances"
    echo -en "\\nLXC hosts(s)::\\n\\n  ${LOCAL_IMAGES[*]}\\n" | $FMT
    if ask_yn "Do you really want to delete all images"; then
        lxc_delete_containers
    fi
}

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
    #lxc image list local:
}

lxc_delete_images_localy() {
    echo
    for i in "${LOCAL_IMAGES[@]}"; do
        info_msg "delete image 'local:$i'"
        lxc image delete "local:$i"
    done
    #lxc image list local:
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
    #lxc list "$HOST_PREFIX"
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
    #lxc list "$HOST_PREFIX"
}


# ----------------------------------------------------------------------------
main "$@"
# ----------------------------------------------------------------------------
