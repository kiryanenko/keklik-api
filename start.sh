#!/usr/bin/env bash

stdout=logs/keklik_api.log
stderr=logs/keklik_api_err.log

daphne keklik.asgi:channel_layer -b 0.0.0.0 -p 8000 -v2 >> ${stdout} 2>> ${stderr} &
python3 manage.py runworker -v2 >> ${stdout} 2>> ${stderr} &
