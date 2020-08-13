#!/bin/bash

cd docker
sudo docker-compose down
cd ..

echo "Tearing down GRE tunnels"
./scripts/teardown-gre.sh
