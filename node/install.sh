#!/bin/bash

cd sig
./env.sh
./install.sh
cd ..

./scripts/udpate.sh

cp ./scripts/sbas.service /lib/systemd/system/
systemctl enable sbas.service
systemctl start sbas.service
