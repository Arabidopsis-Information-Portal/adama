#!/bin/bash

IP=$(./registry/deploy/deploy.sh 2>/dev/null)
./rabbitmq/deploy/deploy.sh peer=$IP
./redis/deploy/deploy.sh peer=$IP
./minion/deploy/deploy.sh peer=$IP
