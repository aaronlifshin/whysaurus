#!/bin/bash
today=$(date "+%Y%m%d")
appcfg.py download_data --url=http://whysaurus.appspot.com/_ah/remote_api --filename=/tmp/whysaurus-prod-$today
appcfg.py upload_data --url=http://localhost:8081/_ah/remote_api --filename=/tmp/whysaurus-prod-$today