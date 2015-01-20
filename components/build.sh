#!/bin/bash

main() {
    local components

    if [[ "$#" == "0" ]]; then
        components=$(ls -d [^_]*/)
    else
        components=("$1")
    fi

    for component in ${components}; do
        echo "Building ${component}:"
        ( cd "${component}/build"; make )
    done
}

main $*
