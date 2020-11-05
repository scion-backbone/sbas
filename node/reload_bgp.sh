#!/bin/bash
sudo systemctl stop sbas.service
./scripts/update_bgp.sh
sudo systemctl start sbas.service
