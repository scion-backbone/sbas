#!/bin/bash
echo "Starting SBAS"
echo "============="

python3 scripts/gen.py

cd docker
docker-compose up -d
iptables -I FORWARD -s 0.0.0.0/0 -j ACCEPT
cd ..

cd sig
./run.sh
cd ..

echo "Setting up GRE tunnels"
./scripts/setup-gre.sh
