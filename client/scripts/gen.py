import json

ROOT_DIR = '.'
GEN_DIR = f'{ROOT_DIR}/gen'
CFG_FILE = f'{ROOT_DIR}/nodes.json'

def gen_wg_conf():
    pass

if __name__ == "__main__":
    with open(CFG_FILE, 'r') as f:
        nodes = json.loads(f.read())
        gen_wg_conf()

