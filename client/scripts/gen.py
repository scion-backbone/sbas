import json
import sys

ROOT_DIR = '..'
GEN_DIR = f'gen'
CFG_FILE = f'{ROOT_DIR}/nodes.json'
DEFAULT_FILE = 'wg0-default.conf'

def gen_wg_conf(name, node, client_ip):
    default = ""
    with open(DEFAULT_FILE, 'r') as f:
        default = f.read()

    node = nodes[name]

    conf = default
    for field in ['vpn-key', 'ext-prefix', 'public-ip']:
        conf = conf.replace('${' + field + '}', node[field])

    conf = conf.replace('${client-ip}', client_ip)

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
        gen_wg_conf(name, nodes[name], client_ip)

