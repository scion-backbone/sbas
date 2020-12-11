#!/bin/bash
DB=../scripts/db.sh
SC=/etc/scion
LOG=/var/log/scion
sigIP=$($DB -l int-sig-ip)

# Copy configs
SIGCONF=${SC}/sig.toml
cp sig.toml ${SIGCONF}
cp ../gen/sig.json ${SC}/sig.json

# Enable service
systemctl enable scion-sig.service
systemctl start scion-sig.service
