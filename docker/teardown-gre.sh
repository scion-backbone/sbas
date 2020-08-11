#!/bin/bash
DB=../db.sh

for remote in $($DB -r); do
    dev=sbas${remote}
    ip rule del from all lookup 10 priority 10
    ip route del $($DB -r ${remote} ext-prefix) dev ${dev} table 10
    ip route del $($DB -l ext-prefix) via 10.99.0.3 table 10

    ip link set ${dev} down
    remote_sig=$($DB -r ${remote} int-sig-ip)
    local_sig=$($DB -l int-sig-ip)
    ip tunnel del ${dev} mode gre remote ${remote_sig} local ${local_sig} ttl 255
done
