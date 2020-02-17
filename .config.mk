# -*- coding: utf-8; mode: makefile-gmake -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This environment is used by Makefile targets.  If you not maintain your own
# searx brand, you normally not need to change the defaults (except SEARX_URL).
# Compare your settings here with file .config.sh used by the toolboxing in
# utils.

export SEARX_URL:=$(or ${SEARX_URL},https://searx.me)

export DOCS_URL:=$(or ${DOCS_URL},https://asciimoo.github.io/searx)
export GIT_URL:=$(or ${GIT_URL},https://github.com/asciimoo/searx)

