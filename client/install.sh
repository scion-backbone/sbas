#!/bin/bash

if (($# < 2)); then
    echo "Usage: ./install.sh node ip"
    exit
fi

python3 scripts/gen.py $1 $2
cp gen/wg0-*.conf /usr/local/etc/wireguard/
