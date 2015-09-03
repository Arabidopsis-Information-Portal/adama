#!/bin/bash

echo
echo "****************************************"
echo "Access notebook in http://<ip>:9999"
echo "Current working directory: host/\$CWD"
echo "****************************************"
echo
mkdir -p /root/.ipython/profile_default
cp ipython_config.py /root/.ipython/profile_default
cd /local/console
ipython notebook --no-browser --port 8888 --ip=*
