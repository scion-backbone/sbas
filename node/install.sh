#!/bin/bash

cd sig
./env.sh
./install.sh
cd ..

cd docker
source ../gen/docker.env
sudo docker-compose build
cd ..

./reload.sh
