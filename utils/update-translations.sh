#!/bin/sh

# script to easily update translation language files

# add new language:
# pybabel init -i messages.pot -d searx/translations -l en

SEARX_DIR='searx'

pybabel extract -F babel.cfg -o messages.pot "$SEARX_DIR"
for f in `ls "$SEARX_DIR"'/translations/'`; do
    pybabel update -N -i messages.pot -d "$SEARX_DIR"'/translations/' -l "$f"
done

echo '[!] update done, edit .po files if required and run pybabel compile -d searx/translations/'
