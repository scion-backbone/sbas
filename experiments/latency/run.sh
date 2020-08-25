#!/bin/bash

ROOT=../..
DIR=$(cd $(dirname $0); pwd -P)

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
./start.sh ${NODE} ${LOCAL_IP}

cd ${DIR}
mkdir -p out
if [ $1 = "A" ]; then
    ping $REMOTE_IP -c 10 -q > out/ping.txt
fi

