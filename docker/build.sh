#!/bin/bash

source set-vars.sh
docker-compose build --build-arg SBAS_VPN_NET=$SBAS_VPN_NET vpn
docker-compose build --build-arg SBAS_VPN_NET=$SBAS_VPN_NET router
