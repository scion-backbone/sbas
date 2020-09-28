#!/bin/bash
INSTALL_DIR=/etc/wireguard/

if (($# < 2)); then
    echo "Usage: ./install.sh node ip"
    exit
fi

mkdir -p ${INSTALL_DIR}
python3 scripts/gen.py $1 $2
for c in gen/wg0-*.conf; do
    chmod 600 ${c}
    cp ${c} ${INSTALL_DIR}
done
