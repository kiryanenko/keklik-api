#!/usr/bin/env bash

pkill daphne
pkill python

pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic -c --no-input

daphne keklik.asgi:channel_layer -b 0.0.0.0 -p 8000 -v2 &
python3 manage.py runworker -v2 &
