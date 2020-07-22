#!/bin/bash

source set-vars.sh

ip tunnel add sbasgre mode gre remote $SBAS_SIG_IP_REMOTE local $SBAS_SIG_IP ttl 255
ip link set sbasgre up

# Since, in the future, traffic other than just traffic to the remote opt in client might go over the SBAS, this line will be a little more complex.
ip route add $SBAS_VPN_NET_REMOTE dev sbasgre

