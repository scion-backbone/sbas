#!/bin/bash
python3 scripts/gen_bgp.py
mkdir -p docker/peering/gen
cp gen/router-run.sh docker/peering/gen/run.sh

cd sig
sudo -E ./configure.sh
cd ..

cd docker
source ../gen/docker.env
sudo docker-compose build
cd ..
