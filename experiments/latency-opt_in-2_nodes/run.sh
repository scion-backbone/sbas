#!/bin/bash

DIR=$(cd $(dirname $0); pwd -P)
ROOT=${DIR}/../..
mkdir -p out

if (($# < 2)); then
    echo "Please provide host name A or B and a public IP address of the other endpoint"
    exit
fi

PING_FLAGS="-c 10" # add -q to suppress individual output
NODE=""
LOCAL=""
LOCAL_VPN=""
REMOTE_SBAS=""
REMOTE_PUBLIC="$2"
if [ $1 = "A" ]; then
    NODE="oregon"
    LOCAL="184.164.236.2"
    LOCAL_VPN="184.164.236.1"
    REMOTE_SBAS="184.164.236.130"
elif [ $1 = "B" ]; then
    NODE="frankfurt"
    LOCAL="184.164.236.130"
    LOCAL_VPN="184.164.237.129"
    REMOTE_SBAS="184.164.236.2"
fi

if [ $1 = "A" ]; then
    echo "Recording Internet baseline..."
    ping ${REMOTE_PUBLIC} ${PING_FLAGS} | tee out/ping-ip.txt
fi

cd ${ROOT}/client
./install.sh ${NODE} ${LOCAL}
./start.sh ${NODE}

echo "Recording latency to SBAS node through VPN tunnel..."
ping ${PING_FLAGS} ${LOCAL_VPN} | tee out/ping-vpn.txt

trap cleanup INT
function cleanup() {
    cd ${ROOT}/client
    ./stop.sh ${NODE}
}

cd ${DIR}
if [ $1 = "A" ]; then
    echo "Pinging through SBAS..."
    ping ${REMOTE_SBAS} ${PING_FLAGS} | tee out/ping-sbas.txt
    cleanup
else
    # Wait forever
    cat
fi

