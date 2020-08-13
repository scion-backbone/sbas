#!/bin/bash

cd sig
./env.sh
./install.sh
cd ..

cd docker/wireguard
sudo docker build -t wireguard:local
cd ../..

./reload.sh
