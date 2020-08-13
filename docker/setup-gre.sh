#!/bin/bash
DB=../db.sh

if [ -z "$SBAS_NODE" ]; then
    echo "Environment variable SBAS_NODE is not set. Make sure to pass the -E flag if you are using sudo."
    exit
fi

for remote in $($DB -r); do
    dev=sbas-${remote}
    remote_sig=$($DB -r ${remote} int-sig-ip)
    local_sig=$($DB -l int-sig-ip)
    ip tunnel add ${dev} mode gre remote ${remote_sig} local ${local_sig} ttl 255
    ip link set ${dev} up

    # Since, in the future, traffic other than just traffic to the remote opt in client might go over the SBAS, this line will be a little more complex.
    ip route add $($DB -r ${remote} ext-prefix) dev ${dev} table 10
    ip route add $($DB -l ext-prefix) via 10.99.0.3 table 10
    ip rule add from all lookup 10 priority 10
done
