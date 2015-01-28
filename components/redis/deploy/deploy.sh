#!/bin/bash

cd $(dirname $0)
if [[ "$1" == "stop" ]]; then
    EXTRA_VARS="--extra-vars \"stop=1\""
    shift
fi
TEMPFILE=$(mktemp || mktemp -t X) 2>/dev/null
for var in $*; do
    EXTRA_VARS="$EXTRA_VARS --extra-vars \"$var\"";
done
EXTRA_VARS="$EXTRA_VARS --extra-vars \"tempfile=$TEMPFILE\""
eval ansible-playbook -i hosts $EXTRA_VARS deploy.yml >&2
cat $TEMPFILE
rm -rf $TEMPFILE
