#!/bin/bash
echo "Starting SBAS"
echo "============="

cd docker
sudo docker-compose up &

echo "Setting up GRE tunnels"
./scripts/setup-gre.sh
