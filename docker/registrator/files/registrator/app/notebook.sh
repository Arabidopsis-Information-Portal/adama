#!/bin/bash

echo
echo "****************************************"
echo "Access notebook in http://<ip>:9999"
echo "Current working directory: host/\$CWD"
echo "****************************************"
echo
ipython notebook --no-browser --port 8888 --ip=*
