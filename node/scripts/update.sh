#!/bin/bash
python3 scripts/gen.py
mkdir -p docker/peering/gen
cp gen/router-run.sh docker/peering_wireguard_merged/gen/run.sh

cd sig
sudo -E ./configure.sh
cd ..

cd docker
source ../gen/docker.env
sudo docker-compose build
cd ..
