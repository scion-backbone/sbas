#!/bin/bash

cd sig
./env.sh
./install.sh
cd ..

./scripts/update.sh

sudo cp ./scripts/sbas.service /lib/systemd/system/
sudo systemctl enable sbas.service
sudo systemctl start sbas.service
