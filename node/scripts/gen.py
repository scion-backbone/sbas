import json
import os

ROOT_DIR = '..'
GEN_DIR = f'gen'
ENV_NODE = 'SBAS_NODE'
CFG_FILE = f'{ROOT_DIR}/nodes.json'

def gen_sshconfig(nodes):
    with open(f"{GEN_DIR}/sshconfig", 'w') as f:
        for name in nodes:
            f.write(f"Host sbas-{name}\n")
            f.write(f"    HostName {nodes[name]['public-ip']}\n")
            f.write(f"    User scionlab\n\n")

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
        }.items():
            write(k, v)

        if 'peering-mux' in local:
            write('ROUTER_MUX', local['peering-mux'])

def gen_routes(local, remote):
    with open(f"{GEN_DIR}/router-run.sh", 'w') as f:
        f.write("#!/bin/bash\n")
        # Route to local customer
        f.write(f"ip route add {local['ext-prefix']} via 10.99.0.2 dev eth0 table 10\n")
        # Routes to remote customers
        for r in remote.values():
            f.write(f"ip route add {r['ext-prefix']} via 10.99.0.1 dev eth0 table 10\n")
        f.write("ip rule add from all lookup 10 priority 10\n")
        if 'peering-mux' in local:
            f.write(f"./peering openvpn up {local['peering-mux']}\n")
        # Docker must have a command to run in foreground, so just add a busy tail
        f.write("tail -F keep-alive\n")

if __name__ == "__main__":
    with open(CFG_FILE, 'r') as f:
        nodes = json.loads(f.read())
        gen_sshconfig(nodes)

        if ENV_NODE in os.environ:
            local_id = os.environ[ENV_NODE]
            if local_id in nodes:
                local = nodes[local_id]
                remote = nodes.copy()
                remote.pop(local_id)

                gen_sig_rules(remote)
                gen_docker_env(local)
                gen_routes(local, remote)
            else:
                print(f"Node '{local_id}' does not exist")
