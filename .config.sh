# -*- coding: utf-8; mode: sh -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# shellcheck shell=bash
#
# This environment is used by ./utils scripts like filtron.sh or searx.sh.  The
# default values are *most flexible* and *best maintained*, you normally not
# need to change the defaults (except PUBLIC_URL).
#
# Before you change any value here you have to uninstall any previous
# installation.  Further is it recommended to backup your changes simply by
# adding them to you local brand (git branch)::
#
#     git add .config
#
# Compare your settings here with file .config.mk used by the Makefile targets.

# The public URL of the searx instance: PUBLIC_URL="https://mydomain.xy/searx"
# The default is taken from the Makefile environment (SEARX_URL).
PUBLIC_URL="${SEARX_URL:-http://$(uname -n)/searx}"
PUBLIC_HOST="${PUBLIC_HOST:-$(echo "$PUBLIC_URL" | sed -e 's/[^/]*\/\/\([^@]*@\)\?\([^:/]*\).*/\2/')}"

# searx.sh
# ---------

SEARX_INTERNAL_URL="${SEARX_INTERNAL_URL:-127.0.0.1:8888}"

# Only change, if you maintain a searx brand in your searx fork.  The default is
# taken from the Makefile environment (DOCS_URL, GIT_URL).
SEARX_DOCS_URL="${DOCS_URL:-https://asciimoo.github.io/searx}"
SEARX_GIT_URL="${GIT_URL:-https://github.com/asciimoo/searx.git}"
SEARX_GIT_BRANCH="${SEARX_GIT_BRANCH:-master}"

# filtron.sh
# ----------

FILTRON_API="${FILTRON_API:-127.0.0.1:4005}"
FILTRON_LISTEN="${FILTRON_LISTEN:-127.0.0.1:4004}"
FILTRON_TARGET="${FILTRON_TARGET:-127.0.0.1:8888}"

# morty.sh
# --------

# morty listen address
MORTY_LISTEN="${MORTY_LISTEN:-127.0.0.1:3000}"

# system services
# ---------------

# **experimental**: Set SERVICE_USER to run all services by one account, but be
# aware that removing discrete components might conflict!
#
# SERVICE_USER=searx

# Common $HOME folder of the service accounts
SERVICE_HOME_BASE="${SERVICE_HOME_BASE:-/usr/local}"

