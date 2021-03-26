#!/bin/bash

PREFIX="/etc/sbas"
sudo mkdir -p $PREFIX

bash -c 'cd sig; ./install.sh'
./scripts/update.sh

sudo -E envsubst < scripts/sbas.service \
    | sudo tee /lib/systemd/system/sbas.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable sbas.service
sudo systemctl start sbas.service
