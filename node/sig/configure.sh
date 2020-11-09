#!/bin/bash
DB=../scripts/db.sh
SC=/etc/scion
LOG=/var/log/scion
sigIP=$($DB -l int-sig-ip)

# Copy services
SIGCONF=${SC}/sig.toml
cp sig.toml ${SIGCONF}
cp ../gen/sig.json ${SC}/sig.json

# Create SIG service
SERVICE=/lib/systemd/system/scion-sig.service
cp sig.service ${SERVICE}
systemctl enable scion-sig.service
systemctl start scion-sig.service
