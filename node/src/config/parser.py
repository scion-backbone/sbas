import os
import json
from . import consts

# Provides an interface to the SBAS configuration at {consts.ETC_DIR}.

nodes = None
local = None
clients = None
config = None

def get_config():
    global config
    if not config:
        with open(os.path.join(consts.ETC_DIR, consts.NODES_FILE), 'r') as f:
            config = json.load(f)
    return config

def get_nodes():
    global nodes
    nodes = get_config()["nodes"]
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

def get_clients():
    global clients
    if not clients:
        with open(os.path.join(consts.ETC_DIR, consts.CLIENTS_FILE), 'r') as c:
            clients = json.load(c)
    return clients

def get_sbas_asn():
   as_number = get_config()["as-number"]
   return as_number

def get_sbas_prefix():
    secure_prefix = get_config()["secure-prefix"]
    return secure_prefix