#!/usr/bin/env bash

stdout=logs/keklik_api.log
stderr=logs/keklik_api_err.log

pkill daphne
pkill python

pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic -c --no-input

./start.sh
