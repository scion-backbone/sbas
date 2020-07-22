#!/bin/bash

ip route add $SBAS_VPN_NET via 10.99.0.2 dev eth0
ip route add $SBAS_VPN_NET_REMOTE via 10.99.0.1 dev eth0
./peering openvpn up $SBAS_ROUTER_MUX
# Could also make BGP announcement and remove ip address from loopback interface.
tail -F keep-alive