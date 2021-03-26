#!/bin/bash

PREFIX="/etc/sbas"
CFG_URL="https://raw.githubusercontent.com/scion-backbone/config/master/nodes.json"

echo "Downloading most recent configuration..."
sudo wget $CFG_URL -O $PREFIX/nodes.json

python3 scripts/gen.py

{
    cd sig
    sudo -E ./configure.sh
}
{
    source gen/docker.env
    cd docker
    sudo docker-compose build
}
