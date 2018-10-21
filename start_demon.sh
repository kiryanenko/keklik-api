#!/bin/bash
start-stop-daemon -Sbvx $PWD/deploy.sh -n keklik_api -d $PWD
