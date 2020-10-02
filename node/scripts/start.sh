#!/bin/bash
echo "Starting SBAS"
echo "============="

python3 scripts/gen.py

cd docker
docker-compose up -d
cd ..

cd sig
./run.sh
cd ..

echo "Setting up GRE tunnels"
./scripts/setup-gre.sh
