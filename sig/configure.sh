#!/bin/bash
DB=../scripts/db.sh
SC=/etc/scion
LOG=/var/log/scion
ISD=$(ls /etc/scion/gen/ | grep ISD | awk -F 'ISD' '{ print $2 }')
AS=$(ls /etc/scion/gen/ISD${ISD}/ | grep AS | awk -F 'AS' '{ print $2 }')
IA=${ISD}-${AS}
IAd=$(echo $IA | sed 's/_/\:/g')
sigIP=$($DB -l int-sig-ip)
sigID='sigSBAS'

ASDIR=${SC}/gen/ISD${ISD}/AS${AS}
SIGDIR=${ASDIR}/sig${IA}-1
SIGCONF=${SIGDIR}/${sigID}.config
sudo cp sig.config $SIGCONF

# Replace variables in config file
for var in 'SC' 'LOG' 'ISD' 'AS' 'IA' 'IAd' 'sigID' 'sigIP'; do
    sudo sed -i "s%\${${var}}%${!var}%g" ${SIGCONF}
done

# Configure AS topology
sudo cp ../gen/sig.json ${SIGDIR}/${sigID}.json
for topo in ${ASDIR}/*/topology.json; do
    sudo -E python3 gen_topo.py ${topo} ${IA}
done

# Set up IP rules
dummyIF='sig'
sudo ip link add ${dummyIF} type dummy
sudo ip addr add ${sigIP}/32 brd + dev ${dummyIF} label ${dummyIF}:0
for prefix in $($DB -r int-prefix); do
    sudo ip rule add to ${prefix} lookup 11 prio 11
done

# Create SIG service
SERVICE=/lib/systemd/system/scion-sig@.service
sudo cp sig.service ${SERVICE}
sudo sed -i "s%\${sigID}%${sigID}%g" ${SERVICE}
sudo systemctl enable scion-sig@${IA}-1.service
sudo systemctl restart scionlab.target
