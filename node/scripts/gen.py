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

def gen_docker_env(local, remote):
    with open(f"{GEN_DIR}/docker.env", 'w') as f:
        ext_prefix = local['ext-prefix']
        ext_prefix_subsize = int(ext_prefix.split('/')[1])

        for k, v in {
            'VPN_NET': ext_prefix,
            'VPN_SERVER_IP': f"{local['ext-vpn-ip']}/{ext_prefix_subsize}",
            'VPN_SERVER_IP_NO_MASK': local['ext-vpn-ip'],
            'ROUTER_MUX': local['peering-mux'],
            'ROUTER_MUX_ANNOUNCE_PREFIX': ext_prefix,
        }.items():
            f.write(f"SBAS_{k}={v}\n")

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
                gen_docker_env(local, nodes)
            else:
                print(f"Node '{local_id}' does not exist")
