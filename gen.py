import json
import argparse

GEN_DIR = 'gen'

def pretty_json(o):
    return json.dumps(o, indent=4, sort_keys=True)

def gen_sshconfig(nodes):
    with open(f"{GEN_DIR}/sshconfig", 'w') as f:
        for node in nodes:
            f.write(f"Host sbas-{node['name']}\n")
            f.write(f"    HostName {node['ip']}\n")
            f.write(f"    User scionlab\n\n")

def gen_sig_rules(local, remote):
    with open(f"{GEN_DIR}/sig.json", 'w') as f:
        cfg = {'ConfigVersion': 9001}
        cfg['ASes'] = {
            node['scion-ia']: {'Nets': [f"{node['vaddr']}/32"]}
            for node in remote
        }
        f.write(pretty_json(cfg))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", "-n", help="local node name")
    args = parser.parse_args()

    with open('nodes.json', 'r') as f:
        nodes = json.loads(f.read())
        gen_sshconfig(nodes)

        if args.node:
            if args.node in [n['name'] for n in nodes]:
                remote = [n for n in nodes if n['name'] != args.node]
                gen_sig_rules(args.node, remote)
            else:
                print(f"Node '{args.node}' does not exist")
