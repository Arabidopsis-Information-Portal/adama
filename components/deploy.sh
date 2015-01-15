#!/bin/bash

IP=$(./rabbitmq/deploy/deploy.sh @../../defaults.yml)
./rabbitmq/deploy/deploy.sh peer=$IP @../../defaults.yml
./redis/deploy/deploy.sh peer=$IP @../../defaults.yml
./minion/deploy/deploy.sh peer=$IP @../../defaults.yml
