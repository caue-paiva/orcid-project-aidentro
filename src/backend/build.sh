#!/usr/bin/env bash
# Script to setup project for render
set -o errexit

BASE_PATH="src/backend/"

pip install -r $BASE_PATH/requirements.txt

python $BASE_PATH/manage.py collectstatic --no-input

python $BASE_PATH/manage.py migrate