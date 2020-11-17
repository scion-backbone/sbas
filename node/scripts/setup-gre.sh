#!/bin/bash
cd $(dirname $0)
DB=./db.sh

if [ -z "$SBAS_NODE" ]; then
    echo "Environment variable SBAS_NODE is not set. Make sure to pass the -E flag if you are using sudo."
    exit
fi

# If this SBAS node is a PEERING point, allow for default routes out of the local gateway.
if [ $($DB -l outbound-gateway) == 'local' ]; then
        ip route add 0.0.0.0/0 via 10.99.0.3 table 20
fi


rule_number=20
for remote in $($DB -r); do
    dev=sbas-${remote}
    remote_sig=$($DB -r ${remote} int-sig-ip)
    local_sig=$($DB -l int-sig-ip)
    ip tunnel add ${dev} mode gre remote ${remote_sig} local ${local_sig} ttl 255
    ip link set ${dev} up

    # Since, in the future, traffic other than just traffic to the remote opt in client might go over the SBAS, this line will be a little more complex.
    ip route add $($DB -r ${remote} ext-prefix) dev ${dev} table 10

    # Allow traffic from remotes to use this outbound gateway.
    if [ $($DB -l outbound-gateway) == 'local' ]; then
        ip rule add iif ${dev} lookup 20 priority ${rule_number}
	rule_number=$((rule_number+1))
    fi
done
if [ $($DB -l outbound-gateway) != 'local' ]; then
    outbound_gateway_dev=sbas-$($DB -l outbound-gateway)
    ip route add 0.0.0.0/0 dev ${outbound_gateway_dev} table 15
    ip rule add from $($DB -l ext-prefix) lookup 15 priority 15
fi

ip route add $($DB -l ext-prefix) via 10.99.0.3 table 10
ip rule add from all lookup 10 priority 10
