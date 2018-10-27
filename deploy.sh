#!/usr/bin/env bash

stdout=logs/deploy.log
stderr=logs/deploy.log

pkill daphne
pkill python

pip3 install -r requirements.txt > ${stdout} 2> ${stderr}
python3 manage.py migrate >> ${stdout} 2>> ${stderr}
python3 manage.py collectstatic -c --no-input >> ${stdout} 2>> ${stderr}

./start.sh
