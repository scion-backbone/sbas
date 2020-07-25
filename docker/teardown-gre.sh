#!/bin/bash

ip rule del from all lookup 10 priority 10
ip route del $SBAS_VPN_NET_REMOTE dev sbasgre table 10
ip route del $SBAS_VPN_NET via 10.99.0.3 table 10

ip link set sbasgre down
ip tunnel del sbasgre mode gre remote $SBAS_SIG_IP_REMOTE local $SBAS_SIG_IP ttl 255

