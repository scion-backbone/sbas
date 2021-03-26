#!/bin/bash

PREFIX="/etc/sbas"
sudo mkdir -p PREFIX

cd sig
./install.sh
cd ..

./scripts/update.sh

sudo -E envsubst < scripts/sbas.service \
    | sudo tee /lib/systemd/system/sbas.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable sbas.service
sudo systemctl start sbas.service
