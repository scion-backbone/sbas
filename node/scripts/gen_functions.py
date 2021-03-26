import json
import os

ROOT_DIR = '..'
GEN_DIR = f'gen'
ENV_NODE = 'SBAS_NODE'

def gen_sig_rules(remote):
    with open(f"{GEN_DIR}/sig.json", 'w') as f:
        cfg = {'ConfigVersion': 9001}
        cfg['ASes'] = {
            node['scion-ia']: {'Nets': [f"{node['int-prefix']}"]}
            for node in remote.values()
        }
        f.write(json.dumps(cfg, indent=2, sort_keys=True))

def gen_docker_env(local):
    with open(f"{GEN_DIR}/docker.env", 'w') as f:
        ext_prefix = local['ext-prefix']
        ext_prefix_subsize = int(ext_prefix.split('/')[1])

        def write(k, v):
            f.write(f"SBAS_{k}={v}\n")

        for k, v in {
            'VPN_NET': ext_prefix,
            'VPN_SERVER_IP': f"{local['ext-vpn-ip']}/{ext_prefix_subsize}",
            'VPN_SERVER_IP_NO_MASK': local['ext-vpn-ip'],
            'VPN_ROUTER_IP_NO_MASK': local['ext-router-ip'],
        }.items():
            write(k, v)

        if 'peering-mux' in local:
            write('ROUTER_MUX', local['peering-mux'])

def gen_routes(local, remote):
    with open(f"{GEN_DIR}/router-run.sh", 'w') as f:
        # Route to local customer: route to wg0 interface
        # f.write(f"ip route add {local['ext-prefix']} via 10.99.0.2 dev eth0 table 10\n") 
        f.write(f"ip route add {local['ext-prefix']} dev wg0 table 10\n")
        # Routes to remote customers
        for r in remote.values():
            f.write(f"ip route add {r['ext-prefix']} via 10.99.0.1 dev eth0 table 10\n")
        f.write("ip rule add from all lookup 10 priority 10\n")
        # This gen routes does not make BGP announcements, so no need to establish the tunnel.
        #if 'peering-mux' in local:
        #    f.write(f"./peering openvpn up {local['peering-mux']}\n")
        # Add an IP on the VPN network so the router can be reached from customer ASes.
        f.write(f"ip addr add {local['ext-router-ip']} dev lo\n")
        # Docker must have a command to run in foreground, so just add a busy tail.
        #f.write("tail -F keep-alive\n")

def gen_routes_bgp(local, remote):
    with open(f"{GEN_DIR}/router-run.sh", 'w') as f:
        f.write("#!/bin/bash\n")
        # Route to local customer
        f.write(f"ip route add {local['ext-prefix']} via 10.99.0.2 dev eth0 table 10\n")
        # Routes to remote customers
        for r in remote.values():
            f.write(f"ip route add {r['ext-prefix']} via 10.99.0.1 dev eth0 table 10\n")
        f.write("ip rule add from all lookup 10 priority 10\n")
        if 'peering-mux' in local and 'peering-prefixes' in local:
            f.write(f"./peering openvpn up {local['peering-mux']}\n")
            f.write(f"./peering bgp start\n")
            for prefixAndNetwork in local['peering-prefixes']:
                # Make the announcement to PEERING
                f.write(f"./peering prefix announce -m {local['peering-mux']} {prefixAndNetwork[0]}\n")
                # Remote the address the PEERING script assigns
                f.write(f"ip addr del {prefixAndNetwork[1]} dev lo\n")
        # Add an IP on the VPN network so the router can be reached from customer ASes.
        f.write(f"ip addr add {local['ext-router-ip']} dev lo\n")
        # Docker must have a command to run in foreground, so just add a busy tail
        f.write("tail -F keep-alive\n")
