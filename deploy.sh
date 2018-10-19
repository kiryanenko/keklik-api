#!/usr/bin/env bash

pkill daphne
pkill python
daphne keklik.asgi:channel_layer -b 0.0.0.0 -p 8000 -v2 &
python manage.py runworker -v2 &
