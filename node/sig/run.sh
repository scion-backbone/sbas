#!/bin/bash
DB=../scripts/db.sh
sigIP=$($DB -l int-sig-ip)
sigIF='sig'

systemctl restart scion-sig.service

# Wait for IF to come up
while ! ip addr show ${sigIF} >/dev/null 2>&1; do
    sleep 1
done

# Delete existing rules
if ! [ -z "$(ip rule list lookup 11)" ]; then
    ip rule del lookup 11
fi

# Set up IP rules
ip link add ${sigIF} type dummy
ip addr add ${sigIP}/32 brd + dev ${sigIF} label ${sigIF}:0
for prefix in $($DB -r int-prefix); do
    ip rule add to ${prefix} lookup 11 prio 11
done

# Set conservative MTU value
# (suggested by https://docs.scionlab.org/content/apps/remote_sig.html)
sudo ip link set mtu 1200 dev sig
