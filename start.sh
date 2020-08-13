#!/bin/bash
echo "Starting SBAS"
echo "============="

cd docker
sudo docker-compose up -d
cd ..

echo "Setting up GRE tunnels"
sudo -E ./scripts/setup-gre.sh
