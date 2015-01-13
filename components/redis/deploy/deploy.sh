#!/bin/bash

EXTRA_VARS="$*"
ansible-playbook -i hosts --extra-vars "\"$EXTRA_VARS\"" deploy.yml
