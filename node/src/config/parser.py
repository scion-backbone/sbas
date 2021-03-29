import os
import json
from . import consts

nodes = None
local = None

def get_nodes():
    global nodes
    if not nodes:
        with open(os.path.join(consts.ETC_DIR, consts.NODES_FILE), 'r') as f:
            nodes = json.load(f)
    return nodes

def get_local_id():
    global local
    if not local:
        with open(os.path.join(consts.ETC_DIR, consts.NODENAME_FILE), 'r') as f:
            local = f.read().strip()
    return local

def get_local_node():
    return get_nodes()[get_local_id()]

def get_remote_nodes():
    nodes = get_nodes()
    remotes = nodes.copy()
    remotes.pop(get_local_id())
    return remotes
