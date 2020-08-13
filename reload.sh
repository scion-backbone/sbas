#!/bin/bash

cd sig
./configure.sh
cd ..

cd docker
sudo docker-compose build
cd ..

./start.sh
