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

today=$(date "+%Y%m%d")
$GAE_ROOT/appcfg.py download_data --url=http://whysaurus.appspot.com/_ah/remote_api --filename=/tmp/whysaurus-prod-$today
$GAE_ROOT/appcfg.py upload_data --url=http://localhost:8081/_ah/remote_api --filename=/tmp/whysaurus-prod-$today