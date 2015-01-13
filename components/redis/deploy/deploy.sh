#!/bin/bash

cd $(dirname $0)
TEMPFILE=$(mktemp || mktemp -t X) 2>/dev/null
EXTRA_VARS="tempfile=$TEMPFILE $*"
eval ansible-playbook -i hosts --extra-vars "\"$EXTRA_VARS\"" deploy.yml >&2
cat $TEMPFILE
rm -rf $TEMPFILE
