#!/bin/bash

./stop.sh

python3 scripts/gen.py

cd sig
./configure.sh
cd ..

cd docker
sudo docker-compose build
cd ..

./start.sh
