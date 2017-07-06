#!/bin/bash
if [ -z "${GAE_ROOT}" ]; then
	dir=$(which dev_appserver.py)
	if [ -n "${dir}" ]; then
		GAE_ROOT=$(dirname $dir)
	fi
fi

if [ -z "${GAE_ROOT}" ]; then
	echo "GAE_ROOT is not set, and couldn't find Google App Engine SDK"
	exit 1
fi

$GAE_ROOT/dev_appserver.py --log_level debug --dev_appserver_log_level debug --port 8081 app.yaml $*
