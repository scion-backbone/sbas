import json
import sys

ROOT_DIR = '..'
GEN_DIR = f'gen'
CFG_FILE = f'{ROOT_DIR}/nodes.json'
DEFAULT_FILE = 'wg0-default.conf'

def gen_wg_conf(name, nodes, client_ip):
    node = nodes[name]

    default = ""
    with open(DEFAULT_FILE, 'r') as f:
        default = f.read()
    conf = default
    for field in ['vpn-key', 'public-ip']:
        conf = conf.replace('${' + field + '}', node[field])

    prefix_length = 24 # TODO: Un-hardcode this
    conf = conf.replace('${client-ip}', f"{client_ip}/{prefix_length}")
    prefixes = ", ".join(nodes[n]['ext-prefix'] for n in nodes if n != name)
    conf = conf.replace('${all-prefixes}', prefixes)

    with open(f"{GEN_DIR}/wg0-{name}.conf", 'w') as f:
        f.write(conf)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Too few arguments")
        sys.exit(1)

    name = sys.argv[1]
    client_ip = sys.argv[2]

    with open(CFG_FILE, 'r') as f:
        nodes = json.loads(f.read())
        gen_wg_conf(name, nodes, client_ip)

