#!/bin/bash
python3 scripts/gen.py
sed -e '/SBAS_STATIC_ROUTES/{r gen/router-run.sh' -e 'd}' docker/peering_wireguard_merged/scripts/run_conf > docker/peering_wireguard_merged/scripts/run

cd sig
sudo -E ./configure.sh
cd ..

cd docker
source ../gen/docker.env
sudo docker-compose build
cd ..
