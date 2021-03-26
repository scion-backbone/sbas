#!/bin/bash

PREFIX="/etc/sbas"
CFG_URL="https://raw.githubusercontent.com/scion-backbone/config/master/nodes.json"

echo "Downloading most recent configuration..."
wget $CFG_URL -o $PREFIX/nodes.json

python3 scripts/gen.py
#cp gen/router-run.sh docker/peering_wireguard_merged/gen/run.sh
sed -i -e '/SBAS_STATIC_ROUTES/{r gen/router-run.sh' -e 'd}' docker/peering_wireguard_merged/scripts/run

cd sig
sudo -E ./configure.sh
cd ..

cd docker
source ../gen/docker.env
sudo docker-compose build
cd ..
