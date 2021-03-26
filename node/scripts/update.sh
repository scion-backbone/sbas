#!/bin/bash

PREFIX="/etc/sbas"
CFG_URL="https://raw.githubusercontent.com/scion-backbone/config/master/nodes.json"

echo "Downloading most recent configuration..."
sudo wget $CFG_URL -O $PREFIX/nodes.json

python3 scripts/gen.py
sed -e '/SBAS_STATIC_ROUTES/{r gen/router-run.sh' -e 'd}' docker/peering_wireguard_merged/scripts/run_conf > docker/peering_wireguard_merged/scripts/run

bash -c 'cd sig; sudo -E ./configure.sh'
bash -c 'source gen/docker.env; cd docker; sudo docker-compose build'
