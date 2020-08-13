#!/bin/bash

cd docker
sudo docker-compose down

echo "Tearing down GRE tunnels"
./scripts/teardown-gre.sh
