#!/bin/sh

help() {
	printf "Command line:\n\n"
	printf "  -h  Display this help\n"
	printf "  -d  Dry run to update the configuration files.\n"
	printf "  -f  Always update on the configuration files (existing files are renamed with the .old suffix)\n"
	printf "      Without this option, the new configuration files are copied with the .new suffix\n"
	printf "\nEnvironment variables:\n\n"
	printf "  INSTANCE_NAME settings.yml : general.instance_name\n"
	printf "  AUTOCOMPLETE  settings.yml : search.autocomplete\n"
	printf "  BASE_URL      settings.yml : server.base_url\n"
	printf "  MORTY_URL     settings.yml : result_proxy.url\n"
	printf "  MORTY_KEY     settings.yml : result_proxy.key\n"
	printf "  BIND_ADDRESS  uwsgi bind to the specified TCP socket using HTTP protocol. Default value: \"${DEFAULT_BIND_ADDRESS}\"\n"
	printf "\nVolume:\n\n"
	printf "  /etc/searx    the docker entry point copies settings.yml and uwsgi.ini in this directory (see the -f command line option)\n"
	echo
	exit 0
}

export DEFAULT_BIND_ADDRESS="0.0.0.0:8080"
if [ -z "${BIND_ADDRESS}" ]; then
    export BIND_ADDRESS="${DEFAULT_BIND_ADDRESS}"
fi

export UWSGI_SETTINGS_PATH=/etc/searx/uwsgi.ini
export SEARX_SETTINGS_PATH=/etc/searx/settings.yml

# Parse special command line
# see docs/admin/installation-docker.rst
# display the help message without the version
if [ "$1" = "help" ]; then
	help
fi

# Version
export SEARX_VERSION=$(su searx -c 'python3 -c "import six; import searx.version; six.print_(searx.version.VERSION_STRING)"' 2>/dev/null)
printf 'searx version %s\n\n' "${SEARX_VERSION}"

# Parse command line
FORCE_CONF_UPDATE=0
DRY_RUN=0
while getopts "fdh" option
do
    case $option in
	f)
	    FORCE_CONF_UPDATE=1
	    ;;
	d)
	    DRY_RUN=1
	    ;;
	h)
		help
    esac
done

# helpers to update the configuration files
patch_uwsgi_settings() {
    CONF="$1"

    # Nothing
}

patch_searx_settings() {
    CONF="$1"

    # Make sure that there is trailing slash at the end of BASE_URL
    # see http://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#Shell-Parameter-Expansion
    export BASE_URL="${BASE_URL%/}/"

    # update settings.yml
    sed -i -e "s|base_url : False|base_url : ${BASE_URL}|g" \
       -e "s/instance_name : \"searx\"/instance_name : \"${INSTANCE_NAME}\"/g" \
       -e "s/autocomplete : \"\"/autocomplete : \"${AUTOCOMPLETE}\"/g" \
       -e "s/ultrasecretkey/$(openssl rand -hex 32)/g" \
       "${CONF}"

    # Morty configuration
    if [ ! -z "${MORTY_KEY}" -a ! -z "${MORTY_URL}" ]; then
	sed -i -e "s/image_proxy : False/image_proxy : True/g" \
	    "${CONF}"
	cat >> "${CONF}" <<-EOF

# Morty configuration
result_proxy:
   url : ${MORTY_URL}
   key : !!binary "${MORTY_KEY}"
EOF
    fi
}

update_conf() {
    FORCE_CONF_UPDATE=$1
    CONF="$2"
    NEW_CONF="${2}.new"
    OLD_CONF="${2}.old"
    REF_CONF="$3"
    PATCH_REF_CONF="$4"

    if [ -f "${CONF}" ]; then
	if [ "${REF_CONF}" -nt "${CONF}" ]; then
	    # There is a new version
	    if [ $FORCE_CONF_UPDATE -ne 0 ]; then
		# Replace the current configuration
		printf '⚠️  Automaticaly update %s to the new version\n' "${CONF}"
		if [ ! -f "${OLD_CONF}" ]; then
		    printf 'The previous configuration is saved to %s\n' "${OLD_CONF}"
		    mv "${CONF}" "${OLD_CONF}"
		fi
		cp "${REF_CONF}" "${CONF}"
		$PATCH_REF_CONF "${CONF}"
	    else
		# Keep the current configuration
		printf '⚠️  Check new version %s to make sure searx is working properly\n' "${NEW_CONF}"
		cp "${REF_CONF}" "${NEW_CONF}"
		$PATCH_REF_CONF "${NEW_CONF}"
	    fi
	else
	    printf 'Use existing %s\n' "${CONF}"
	fi
    else
	printf 'Create %s\n' "${CONF}"
	cp "${REF_CONF}" "${CONF}"
	$PATCH_REF_CONF "${CONF}"
    fi
}

# make sure there are uwsgi settings
update_conf ${FORCE_CONF_UPDATE} "${UWSGI_SETTINGS_PATH}" "/usr/local/searx/dockerfiles/uwsgi.ini" "patch_uwsgi_settings"

# make sure there are searx settings
update_conf "${FORCE_CONF_UPDATE}" "${SEARX_SETTINGS_PATH}" "/usr/local/searx/searx/settings.yml" "patch_searx_settings"

# dry run (to update configuration files, then inspect them)
if [ $DRY_RUN -eq 1 ]; then
    printf 'Dry run\n'
    exit
fi

#
touch /var/run/uwsgi-logrotate
chown -R searx:searx /var/log/uwsgi /var/run/uwsgi-logrotate
unset MORTY_KEY

# Start uwsgi
printf 'Listen on %s\n' "${BIND_ADDRESS}"
exec su-exec searx:searx uwsgi --master --http-socket "${BIND_ADDRESS}" "${UWSGI_SETTINGS_PATH}"
