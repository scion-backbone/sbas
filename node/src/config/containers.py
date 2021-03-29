import os
import subprocess

from . import parser
from . import consts

def get_env():
    local = parser.get_local_node()
    
    ext_prefix = local['ext-prefix']
    ext_prefix_subsize = int(ext_prefix.split('/')[1])

    env = {
        'VPN_NET': ext_prefix,
        'VPN_SERVER_IP': f"{local['ext-vpn-ip']}/{ext_prefix_subsize}",
        'VPN_SERVER_IP_NO_MASK': local['ext-vpn-ip'],
        'VPN_ROUTER_IP_NO_MASK': local['ext-router-ip'],
    }

    if 'peering-mux' in local:
        env['ROUTER_MUX'] = local['peering-mux']
    
    return env

container_dir = os.path.join(consts.DOCKER_DIR, 'peering_wireguard')
gen_path = os.path.join(container_dir, 'scripts', 'setup-peering.sh')

def _update_routes():
    local = parser.get_local_node()
    remotes = parser.get_remote_nodes()

    with open(gen_path, 'w') as f:
        f.write("#!/bin/bash\n")
        # Route to local customer
        f.write(f"ip route add {local['ext-prefix']} via 10.99.0.2 dev eth0 table 10\n")

        # Routes to remote customers
        for r in remotes.values():
            f.write(f"ip route add {r['ext-prefix']} via 10.99.0.1 dev eth0 table 10\n")
        f.write("ip rule add from all lookup 10 priority 10\n")

        if 'peering-mux' in local and 'peering-prefixes' in local:
            f.write(f"./peering openvpn up {local['peering-mux']}\n")
            f.write(f"./peering bgp start\n")
            for prefixAndNetwork in local['peering-prefixes']:
                # Make the announcement to PEERING
                f.write(f"./peering prefix announce -m {local['peering-mux']} {prefixAndNetwork[0]}\n")
                # Remove the address the PEERING script assigns
                f.write(f"ip addr del {prefixAndNetwork[1]} dev lo\n")

        # Add an IP on the VPN network so the router can be reached from customer ASes.
        f.write(f"ip addr add {local['ext-router-ip']} dev lo\n")

def update():
    _update_routes()