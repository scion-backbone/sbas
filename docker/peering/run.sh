#!/bin/bash

ip route add $SBAS_VPN_NET via 10.99.0.2 dev eth0 table 10
ip route add $SBAS_VPN_NET_REMOTE via 10.99.0.1 dev eth0 table 10
ip rule add from all lookup 10 priority 10
./peering openvpn up $SBAS_ROUTER_MUX
# Could also make BGP announcement and remove ip address from loopback interface.
tail -F keep-alive