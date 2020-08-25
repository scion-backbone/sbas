#!/bin/bash

./stop.sh

python3 scripts/gen.py

cd sig
./configure.sh
cd ..

cd docker
source ../gen/docker.env
sudo docker-compose build
cd ..

./start.sh
