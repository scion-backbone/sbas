#!/bin/bash

cd docker
sudo docker-compose down
cd ..

echo "Tearing down GRE tunnels"
sudo -E ./scripts/teardown-gre.sh
