import json
import os

GEN_DIR = 'gen'
ENV_NODE = 'SBAS_NODE'

def gen_sshconfig(nodes):
    with open(f"{GEN_DIR}/sshconfig", 'w') as f:
        for name in nodes:
            f.write(f"Host sbas-{name}\n")
            f.write(f"    HostName {nodes[name]['ip']}\n")
            f.write(f"    User scionlab\n\n")

def gen_sig_rules(local, remote):
    with open(f"{GEN_DIR}/sig.json", 'w') as f:
        cfg = {'ConfigVersion': 9001}
        cfg['ASes'] = {
            node['scion-ia']: {'Nets': [f"{node['vaddr']}/32"]}
            for node in remote
        }
        f.write(json.dumps(cfg, indent=2, sort_keys=True))

if __name__ == "__main__":
    with open('nodes.json', 'r') as f:
        nodes = json.loads(f.read())
        gen_sshconfig(nodes)

        if ENV_NODE in os.environ:
            local = os.environ[ENV_NODE]
            if local in nodes:
                nodes.pop(local)
                gen_sig_rules(local, remote)
            else:
                print(f"Node '{local}' does not exist")
