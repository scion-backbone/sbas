#!/bin/bash

DIR=$(cd $(dirname $0); pwd -P)
ROOT=${DIR}/../..

if (($# < 1)); then
    echo "Please provide host name A or B"
    exit
fi

NODE=""
LOCAL_IP=""
REMOTE_IP=""
if [ $1 = "A" ]; then
    NODE="oregon"
    LOCAL_IP="184.164.236.2"
    REMOTE_IP="184.164.237.2"
elif [ $1 = "B" ]; then
    NODE="frankfurt"
    LOCAL_IP="184.164.237.2"
    REMOTE_IP="184.164.236.2"
fi

cd ${ROOT}/client
./install.sh ${NODE} ${LOCAL_IP}
./start.sh ${NODE}

trap cleanup INT
function cleanup() {
    cd ${ROOT}/client
    ./stop.sh ${NODE}
}

cd ${DIR}
mkdir -p out
if [ $1 = "A" ]; then
    ping $REMOTE_IP -c 10 -q > out/ping.txt
else
    # Wait forever
    cat
fi

