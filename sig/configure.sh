export SC=/etc/scion
export LOG=/var/log/scion
export ISD=$(ls /etc/scion/gen/ | grep ISD | awk -F 'ISD' '{ print $2 }')
export AS=$(ls /etc/scion/gen/ISD${ISD}/ | grep AS | awk -F 'AS' '{ print $2 }')
export IA=${ISD}-${AS}
export IAd=$(echo $IA | sed 's/_/\:/g')
export sigIP=$(python3 -c "import json; f = open('../nodes.json', 'r'); print(json.load(f)['$SBAS_NODE']['sig']); f.close()")
export sigID='sigSBAS'

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
# TODO: Make these persistent
dummyIF='sigdummy'
sudo ip link add ${dummyIF} type dummy
sudo ip addr add ${sigIP}/32 brd + dev ${dummyIF} label ${dummyIF}:0
sudo ip rule add to 172.16.0.0/24 lookup 11 prio 11 # TODO: remove hardcoded subnet

# Create SIG service
SERVICE=/lib/systemd/system/scion-sig@.service
sudo cp sig.service ${SERVICE}
sudo sed -i "s%\${sigID}%${sigID}%g" ${SERVICE}
sudo systemctl enable scion-sig@${IA}-1.service
sudo systemctl restart scionlab.target
