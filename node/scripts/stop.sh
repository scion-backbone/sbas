#!/bin/bash

cd docker
docker-compose down
cd ..

echo "Tearing down GRE tunnels"
./scripts/teardown-gre.sh