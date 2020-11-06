#!/bin/bash
DB=../scripts/db.sh
sigIP=$($DB -l int-sig-ip)
dummyIF='sig'

# Delete existing configuration (if exists)
ip link list ${dummyIF} >/dev/null 2>&1
if [ $? = 0 ]; then
    ip link del ${dummyIF}
fi
if ! [ -z "$(ip rule list lookup 11)" ]; then
    ip rule del lookup 11
fi

# Set up IP rules
ip link add ${dummyIF} type dummy
ip addr add ${sigIP}/32 brd + dev ${dummyIF} label ${dummyIF}:0
for prefix in $($DB -r int-prefix); do
    ip rule add to ${prefix} lookup 11 prio 11
done

systemctl restart scion-sig.service
