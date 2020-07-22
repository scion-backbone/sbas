#!/bin/bash

ip route add $SBAS_VPN_NET via 10.99.0.2 dev eth0
./peering openvpn up $SBAS_ROUTER_MUX
# Could also make BGP announcement and remove ip address from loopback interface.
tail -F keep-alive