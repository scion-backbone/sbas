#!/bin/bash
sudo systemctl stop sbas.service
./scripts/update.sh
sudo systemctl start sbas.service
