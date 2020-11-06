#!/bin/bash
DB=../scripts/db.sh
SC=/etc/scion
LOG=/var/log/scion
sigIP=$($DB -l int-sig-ip)

SIGCONF=${SC}/sig.toml
cp sig.toml ${SIGCONF}

# Replace variables in config file
for var in 'SC' 'LOG' 'ISD' 'AS' 'IA' 'IAd' 'sigID' 'sigIP'; do
    sudo sed -i "s%\${${var}}%${!var}%g" ${SIGCONF}
done

# Create SIG service
SERVICE=/lib/systemd/system/scion-sig.service
cp sig.service ${SERVICE}
systemctl enable scion-sig.service
