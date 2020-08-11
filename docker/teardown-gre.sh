#!/bin/bash
DB=../db.sh

for remote in $($DB -r); do
    ip rule del from all lookup 10 priority 10
    ip route del $($DB -r ext-prefix) dev sbasgre table 10
    ip route del $($DB -l ext-prefix) via 10.99.0.3 table 10

    ip link set sbasgre down
    ip tunnel del sbasgre mode gre remote $($DB -r int-sig-ip) local $($DB -l int-sig-ip) ttl 255
done
